import os
from pyspark.sql import *
aws_access_key_id = os.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.get('AWS_SECRET_ACCESS_KEY')

myspark = SparkSession\
          .builder\
          .master("local[1]")\
          .appName("Country App2")\
	  .config("spark.hadoop.fs.s3a.endpoint", "s3.us-east-2.amazonaws.com")\
          .getOrCreate()

myspark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.access.key", AWS_ACCESS_KEY_ID)
myspark.sparkContext._jsc.hadoopConfiguration().set("fs.s3a.secret.key", AWS_SECRET_ACCESS_KEY)
myspark.sparkContext._jsc.hadoopConfiguration().set("com.amazonaws.services.s3.enableV4", "true")
myspark.sparkContext.setSystemProperty("com.amazonaws.services.s3.enableV4", "true")


df = myspark.read.format("com.mongodb.spark.sql.DefaultSource").option("spark.mongodb.input.uri","mongodb://172.18.0.3:27017/new_data.country_data?authSource=admin").load()


df.write.mode("overwrite").json("s3a://awsbuc01/sparktest/content.json")
