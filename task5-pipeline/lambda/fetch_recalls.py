import logging
import os
from nhtsa_fetcher import fetch_all_recalls
from db import get_connection, upsert_recalls, get_record_count

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info("Starting NHTSA recall pipeline")
    
    try:
        # Step 1: Fetch all recalls from NHTSA API
        logger.info("Fetching recalls from NHTSA API...")
        records = fetch_all_recalls()
        logger.info(f"Fetched {len(records)} records from API")
        
        # Step 2: Connect to database
        conn = get_connection()
        
        # Step 3: Upsert records
        upsert_recalls(conn, records)
        logger.info(f"Upserted {len(records)} records into database")
        
        # Step 4: Get total count
        count = get_record_count(conn)
        logger.info(f"Total records in database: {count}")
        
        conn.close()
        
        # Step 5: Return status
        return {
            "statusCode": 200,
            "records_fetched": len(records),
            "total_in_db": count
        }
    
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    result = handler({}, {})
    print(result)