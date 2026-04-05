/**
 * CDK Stack: Data Harmonizer DynamoDB Tables
 *
 * Creates the DynamoDB tables for the data-harmonizer skill:
 * - ohanafy-{env}-mappings: Per-customer approved column mappings
 * - ohanafy-{env}-harmonizer-log: Upload, mapping, and approval event log
 *
 * Stack naming: ohanafy-{env}-data-harmonizer-stack
 */

import * as cdk from "aws-cdk-lib";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import { Construct } from "constructs";

interface DataHarmonizerStackProps extends cdk.StackProps {
  environment: "dev" | "staging" | "prod";
}

export class DataHarmonizerStack extends cdk.Stack {
  public readonly mappingsTable: dynamodb.Table;
  public readonly logTable: dynamodb.Table;

  constructor(scope: Construct, id: string, props: DataHarmonizerStackProps) {
    super(scope, id, {
      ...props,
      tags: {
        "ohanafy:environment": props.environment,
        "ohanafy:team": "ai-ops",
        "ohanafy:managed-by": "cdk",
        "ohanafy:service": "data-harmonizer",
      },
    });

    const env = props.environment;

    // --- Mappings Table ---
    // Stores approved column mappings per customer.
    // PK: customer_id, SK: timestamp
    // GSI: batch_id for rollback lookups
    this.mappingsTable = new dynamodb.Table(this, "MappingsTable", {
      tableName: `ohanafy-${env}-mappings`,
      partitionKey: {
        name: "customer_id",
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: "timestamp",
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      pointInTimeRecovery: true,
      removalPolicy:
        env === "prod"
          ? cdk.RemovalPolicy.RETAIN
          : cdk.RemovalPolicy.DESTROY,
    });

    this.mappingsTable.addGlobalSecondaryIndex({
      indexName: "batch-id-index",
      partitionKey: {
        name: "batch_id",
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: "timestamp",
        type: dynamodb.AttributeType.STRING,
      },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // --- Harmonizer Log Table ---
    // Stores all events: uploads, mapping decisions, confidence scores,
    // corrections, approvals, rollbacks.
    // PK: batch_id, SK: event_type#timestamp
    this.logTable = new dynamodb.Table(this, "HarmonizerLogTable", {
      tableName: `ohanafy-${env}-harmonizer-log`,
      partitionKey: {
        name: "batch_id",
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: "event_key",
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      pointInTimeRecovery: true,
      removalPolicy:
        env === "prod"
          ? cdk.RemovalPolicy.RETAIN
          : cdk.RemovalPolicy.DESTROY,
      timeToLiveAttribute: "ttl",
    });

    // GSI for querying by customer across batches
    this.logTable.addGlobalSecondaryIndex({
      indexName: "customer-id-index",
      partitionKey: {
        name: "customer_id",
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: "timestamp",
        type: dynamodb.AttributeType.STRING,
      },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // --- Outputs ---
    new cdk.CfnOutput(this, "MappingsTableName", {
      value: this.mappingsTable.tableName,
      description: "DynamoDB table for approved column mappings",
    });

    new cdk.CfnOutput(this, "LogTableName", {
      value: this.logTable.tableName,
      description: "DynamoDB table for harmonizer event log",
    });
  }
}
