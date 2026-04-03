#!/bin/bash
set -euo pipefail

# connect-org.sh — Connect to a Salesforce org, retrieve metadata, generate snapshot
# Usage: bash scripts/connect-org.sh <customer-name> [--sandbox|--production] [--type customer|template|sandbox]
# Non-interactive mode: bash scripts/connect-org.sh gulf --production --type customer

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Argument parsing ---
CUSTOMER_NAME="${1:-}"
ENV_NAME=""
ORG_TYPE=""

if [ -z "$CUSTOMER_NAME" ]; then
  echo "Usage: $0 <customer-name> [--sandbox|--production] [--type customer|template|sandbox]"
  echo ""
  echo "Examples:"
  echo "  $0 gulf --production --type customer"
  echo "  $0 ohanafy --sandbox --type sandbox"
  echo "  $0 gulf                    # interactive prompts"
  exit 1
fi
shift

while [[ $# -gt 0 ]]; do
  case $1 in
    --sandbox)    ENV_NAME="sandbox"; shift ;;
    --production) ENV_NAME="production"; shift ;;
    --type)       ORG_TYPE="$2"; shift 2 ;;
    *)            echo "Unknown option: $1"; exit 1 ;;
  esac
done

# --- Interactive fallbacks ---
if [ -z "$ORG_TYPE" ]; then
  echo "What type of org is this?"
  select org_type in "Customer Org" "Template Org" "Development/Sandbox Org"; do
    case $org_type in
      "Customer Org")           ORG_TYPE="customer"; break ;;
      "Template Org")           ORG_TYPE="template"; break ;;
      "Development/Sandbox Org") ORG_TYPE="sandbox"; break ;;
    esac
  done
fi

if [ -z "$ENV_NAME" ]; then
  echo "Which environment?"
  select env in "Sandbox" "Production"; do
    case $env in
      "Sandbox")    ENV_NAME="sandbox"; break ;;
      "Production") ENV_NAME="production"; break ;;
    esac
  done
fi

# --- Derived paths ---
# Customer and sandbox orgs go to customers/<name>/orgs/<env>/
# Template orgs go to projects/<name>/<env>/
case "$ORG_TYPE" in
  customer) BASE_DIR="customers/${CUSTOMER_NAME}/orgs" ;;
  sandbox)  BASE_DIR="customers/${CUSTOMER_NAME}/orgs" ;;
  template) BASE_DIR="projects/${CUSTOMER_NAME}" ;;
esac

ORG_DIR="${REPO_ROOT}/${BASE_DIR}/${ENV_NAME}"
ALIAS="${CUSTOMER_NAME}-${ENV_NAME}"

case "$ENV_NAME" in
  sandbox)    LOGIN_URL="https://test.salesforce.com" ;;
  production) LOGIN_URL="https://login.salesforce.com" ;;
esac

API_VERSION="65.0"

# --- Setup project directory ---
echo "Setting up ${ALIAS} in ${ORG_DIR}..."
mkdir -p "${ORG_DIR}/force-app/main/default"

cat > "${ORG_DIR}/sfdx-project.json" << EOL
{
  "packageDirectories": [{ "path": "force-app", "default": true }],
  "namespace": "",
  "sfdcLoginUrl": "${LOGIN_URL}",
  "sourceApiVersion": "${API_VERSION}"
}
EOL

# --- Authentication ---
# Check if already authenticated
if sf org display --target-org "$ALIAS" &>/dev/null; then
  echo "Already authenticated as ${ALIAS}"
else
  echo "Authenticating with ${ENV_NAME} org..."
  sf org login web --instance-url "${LOGIN_URL}" --alias "${ALIAS}"
fi

sf config set target-org="${ALIAS}" --location project 2>/dev/null || true

# --- Retrieve metadata ---
cd "${ORG_DIR}"

echo "Generating manifest from org..."
sf project generate manifest --output-dir . --from-org "${ALIAS}" --name "package" 2>/dev/null || true

if [ ! -f "./package.xml" ]; then
  echo "Manifest generation failed. Using comprehensive default..."
  cat > "./package.xml" << EOL
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
  <types><members>*</members><name>ApexClass</name></types>
  <types><members>*</members><name>ApexTrigger</name></types>
  <types><members>*</members><name>CustomObject</name></types>
  <types><members>*</members><name>CustomField</name></types>
  <types><members>*</members><name>ValidationRule</name></types>
  <types><members>*</members><name>Flow</name></types>
  <types><members>*</members><name>LightningComponentBundle</name></types>
  <types><members>*</members><name>AuraDefinitionBundle</name></types>
  <types><members>*</members><name>CustomMetadata</name></types>
  <types><members>*</members><name>GlobalValueSet</name></types>
  <types><members>*</members><name>RecordType</name></types>
  <types><members>*</members><name>WorkflowRule</name></types>
  <types><members>*</members><name>WorkflowFieldUpdate</name></types>
  <types><members>*</members><name>WorkflowAlert</name></types>
  <types><members>*</members><name>DuplicateRule</name></types>
  <types><members>*</members><name>MatchingRule</name></types>
  <types><members>*</members><name>SharingCriteriaRule</name></types>
  <types><members>*</members><name>SharingOwnerRule</name></types>
  <types><members>*</members><name>Profile</name></types>
  <types><members>*</members><name>PermissionSet</name></types>
  <types><members>*</members><name>Layout</name></types>
  <types><members>*</members><name>FlexiPage</name></types>
  <types><members>*</members><name>CustomApplication</name></types>
  <types><members>*</members><name>EmailTemplate</name></types>
  <types><members>*</members><name>AssignmentRule</name></types>
  <types><members>*</members><name>EscalationRule</name></types>
  <version>${API_VERSION}</version>
</Package>
EOL
fi

# Ensure critical types use wildcards
CRITICAL_TYPES=("ApexClass" "ApexTrigger" "Flow" "ValidationRule" "CustomObject" "CustomField" "LightningComponentBundle" "AuraDefinitionBundle")
for mtype in "${CRITICAL_TYPES[@]}"; do
  if grep -q "<name>${mtype}</name>" "./package.xml"; then
    # Already present — ensure wildcard
    python3 -c "
import re, sys
with open('./package.xml') as f: content = f.read()
pattern = r'(<types>\s*(?:<members>[^<]*</members>\s*)*<name>${mtype}</name>\s*</types>)'
replacement = '<types><members>*</members><name>${mtype}</name></types>'
content = re.sub(pattern, replacement, content)
with open('./package.xml', 'w') as f: f.write(content)
" 2>/dev/null || true
  fi
done

echo "Retrieving source from ${ALIAS}..."
sf project retrieve start --target-org "${ALIAS}" --manifest ./package.xml || {
  echo "Full retrieve failed. Trying critical types only..."
  sf project retrieve start --target-org "${ALIAS}" --metadata ApexClass ApexTrigger Flow CustomObject LightningComponentBundle
}

# --- Detect installed OHFY packages ---
echo ""
echo "Detecting installed Ohanafy packages..."
PACKAGES_FOUND=()

# Check for ohfy__ namespace classes
if find force-app -name "*.cls" 2>/dev/null | xargs grep -l "ohfy__" 2>/dev/null | head -1 | grep -q .; then
  echo "  Found ohfy__ namespace references"
fi

# Detect SKUs by class name patterns (bash 3.2 compatible)
SKU_NAMES=("OMS" "WMS" "REX" "Ecom" "Payments" "Configure" "EDI" "Planogram")
SKU_PATTERNS=(
  'Order_.*Service\|OrderItem\|Fulfillment'
  'Warehouse\|Inventory.*Service\|Pick\|Pack\|Ship'
  'Display\|Retail\|Equipment\|Route.*Account'
  'Ecommerce\|Shopify\|WooCommerce\|Cart'
  'Payment\|Settlement\|Refund'
  'Configuration\|PackageInstall\|Setup'
  'EDI\|X12\|AS2\|Trading.*Partner'
  'Planogram\|Shelf\|PlacementLayout'
)

idx=0
for sku in "${SKU_NAMES[@]}"; do
  pattern="${SKU_PATTERNS[$idx]}"
  if find force-app -name "*.cls" -o -name "*.trigger" 2>/dev/null | xargs grep -l "$pattern" 2>/dev/null | head -1 | grep -q .; then
    PACKAGES_FOUND+=("$sku")
    echo "  Detected: OHFY-${sku}"
  fi
  idx=$((idx + 1))
done

# --- Generate org snapshot ---
echo ""
echo "Generating org snapshot..."

SNAPSHOT_FILE="${ORG_DIR}/org-snapshot.md"
SNAPSHOT_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)

APEX_COUNT=$(find force-app -name "*.cls" 2>/dev/null | wc -l | tr -d ' ')
TRIGGER_COUNT=$(find force-app -name "*.trigger" 2>/dev/null | wc -l | tr -d ' ')
FLOW_COUNT=$(find force-app -name "*.flow-meta.xml" 2>/dev/null | wc -l | tr -d ' ')
LWC_COUNT=$(find force-app -path "*/lwc/*" -name "*.js" -not -name "*.test.js" 2>/dev/null | wc -l | tr -d ' ')
OBJECT_COUNT=$(find force-app -name "*.object-meta.xml" 2>/dev/null | wc -l | tr -d ' ')
VALIDATION_COUNT=$(find force-app -name "*.validationRule-meta.xml" 2>/dev/null | wc -l | tr -d ' ')
FIELD_COUNT=$(find force-app -name "*.field-meta.xml" 2>/dev/null | wc -l | tr -d ' ')

cat > "$SNAPSHOT_FILE" << SNAPSHOT
# Org Snapshot: ${ALIAS}

- **Generated:** ${SNAPSHOT_DATE}
- **Org Type:** ${ORG_TYPE}
- **Environment:** ${ENV_NAME}
- **Login URL:** ${LOGIN_URL}
- **API Version:** ${API_VERSION}
- **Detected SKUs:** ${PACKAGES_FOUND[*]:-none detected}

## Metadata Summary

| Type | Count |
|------|-------|
| Apex Classes | ${APEX_COUNT} |
| Apex Triggers | ${TRIGGER_COUNT} |
| Flows | ${FLOW_COUNT} |
| LWC Components | ${LWC_COUNT} |
| Custom Objects | ${OBJECT_COUNT} |
| Validation Rules | ${VALIDATION_COUNT} |
| Custom Fields | ${FIELD_COUNT} |

## Ohanafy Objects

$(find force-app -name "*.object-meta.xml" 2>/dev/null | sed 's|.*/||; s|\.object-meta\.xml||' | sort | while read obj; do
  fields=$(find "force-app/main/default/objects/${obj}/fields" -name "*.field-meta.xml" 2>/dev/null | wc -l | tr -d ' ')
  validations=$(find "force-app/main/default/objects/${obj}/validationRules" -name "*.validationRule-meta.xml" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$fields" -gt 0 ] || [ "$validations" -gt 0 ]; then
    echo "- **${obj}**: ${fields} fields, ${validations} validation rules"
  fi
done)

## Apex Triggers

$(find force-app -name "*.trigger" 2>/dev/null | sed 's|.*/||; s|\.trigger||' | sort | while read t; do echo "- ${t}"; done)

## Flows

$(find force-app -name "*.flow-meta.xml" 2>/dev/null | sed 's|.*/||; s|\.flow-meta\.xml||' | sort | while read f; do echo "- ${f}"; done)

## Quick Commands

\`\`\`bash
# Re-retrieve latest metadata
sf project retrieve start --target-org ${ALIAS} --manifest ./package.xml

# Run all Apex tests
sf apex run test --target-org ${ALIAS} --test-level RunLocalTests --wait 10

# Open the org in browser
sf org open --target-org ${ALIAS}

# Query records
sf data query --target-org ${ALIAS} --query "SELECT Id, Name FROM Account LIMIT 10"
\`\`\`
SNAPSHOT

echo ""
echo "Org snapshot saved to: ${SNAPSHOT_FILE}"
echo ""
echo "Setup complete: ${ORG_DIR}"
echo "  Apex: ${APEX_COUNT} | Triggers: ${TRIGGER_COUNT} | Flows: ${FLOW_COUNT} | LWC: ${LWC_COUNT}"
echo "  Objects: ${OBJECT_COUNT} | Fields: ${FIELD_COUNT} | Validations: ${VALIDATION_COUNT}"
echo "  SKUs detected: ${PACKAGES_FOUND[*]:-none}"
