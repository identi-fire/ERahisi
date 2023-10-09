###my imports ##
from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, col, date_format


def startSpark():
    spark = SparkSession \
        .builder \
        .appName('systegra_loans') \
        .getOrCreate()
    return spark



spark = startSpark()



Dfservice_loans= spark.read.parquet('maprfs:////iswdatalake/lending_service/loans/*/*/*/*.parquet')
Dfservice_channels= spark.read.parquet('maprfs://///iswdatalake/lending_service/channels/*.parquet')

 

Dfservice_loans.createOrReplaceTempView("Dfservice_loans")

Dfservice_channels.createOrReplaceTempView("Dfservice_channels")




dfsystegra_loansFinal = spark.sql("""
        select
            A.transformed_date_created,
            A.provider_code,
            A.provider_id,
            SUM(CAST(A.amount as float)/100.0) as value,
            SUM(CAST(A.amount_payable as float)/100.0) as paid_back,
            COUNT(A.provider_code) as Volume,
            A.status,
            B.type as Channel,
            A.tenure,
            A.channel_code,
            B.description,
            A.service_type

            FROM Dfservice_loans A

            LEFT JOIN Dfservice_channels B
            ON A.channel_id = B.id

            GROUP BY
            A.transformed_date_created,
            A.provider_code,
            A.provider_id,
            A.tenure,
            A.channel_code,
            B.type,
            A.status,
            A.service_type,
            B.description

            ORDER BY COUNT(A.transformed_date_created)
            """  )


print(dfsystegra_loansFinal.show(5))
print('writing to mapr')

dfsystegra_loansDF =  dfsystegra_loansFinal \
                .withColumn("transformed_date_created_temp", to_timestamp(col("transformed_date_created"), "yyyy-MM-dd"))\
                .withColumn("year", date_format(col("transformed_date_created"), "yyyy"))\
                .withColumn("month", date_format(col("transformed_date_created"), "MM"))\
                .withColumn("day", date_format(col("transformed_date_created"), "dd"))\
                .drop("transformed_date_created_temp")

try:
    
    dfsystegra_loansDF.repartition(1)\
    .write\
    .partitionBy("year", "month", "day")\
    .mode("append")\
    .parquet("maprfs:///iswdatalake/Systegra/systegra_loans/")

    dfsystegra_loansDF.repartition(1)\
      .write\
      .format("jdbc")\
      .option("url", "jdbc:sqlserver://172.37.1.126:1433;databaseName={BigData_Aggregates}")\
      .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver")\
      .option("database", "BigData_Aggregates").option("dbtable", "dbo.systegra_loans")\
      .option("user", "dataadmin")\
      .option("password", "S3cur3Pass7")\
      .mode("overwrite")\
      .save()

except Exception as e:
    print(e)
