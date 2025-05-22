from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, IntegerType, FloatType, BooleanType
from pyspark.sql.functions import col, from_json, when, current_timestamp

# Definicja schematu JSON
schema = StructType() \
    .add("city", StringType()) \
    .add("timestamp", IntegerType()) \
    .add("temp", FloatType()) \
    .add("pressure", IntegerType()) \
    .add("humidity", IntegerType()) \
    .add("condition", StringType()) \
    .add("alert_24h", BooleanType()) \
    .add("lat", FloatType()) \
    .add("lon", FloatType())

# Inicjalizacja Spark
spark = SparkSession.builder \
    .appName("WeatherStreamProcessor") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Odczyt strumienia z Kafka
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "weather") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

# Parsowanie wartości JSON
json_df = raw_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

def write_all_weather(batch_df, batch_id):
    batch_df.write.mode("overwrite").json("data/all_weather/")

def write_anomalies(batch_df, batch_id):
    anomalies_df = batch_df.withColumn(
        "anomaly_reason",
        when(col("temp") < -5, "temperature_too_low")
        .when(col("temp") > 35, "temperature_too_high")
        .when(col("condition") == "storm", "storm_condition")
    ).filter(col("anomaly_reason").isNotNull())

    anomalies_df.write.mode("append").json("data/anomalies/")

def write_alerts(batch_df, batch_id):
    alerts_df = batch_df.filter(col("alert_24h") == True) \
        .withColumn("alert_issued_at", current_timestamp())

    alerts_df.write.mode("append").json("data/alerts/")


# Rejestracja wszystkich zapytań
json_df.writeStream \
    .foreachBatch(write_all_weather) \
    .outputMode("append") \
    .start()

json_df.writeStream \
    .foreachBatch(write_anomalies) \
    .outputMode("append") \
    .start()

json_df.writeStream \
    .foreachBatch(write_alerts) \
    .outputMode("append") \
    .start() \
    .awaitTermination()
