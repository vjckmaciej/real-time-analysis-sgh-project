FROM bitnami/spark:3.4.1

# Przejście na katalog roboczy
WORKDIR /app

# Skopiuj kod aplikacji
COPY . /app

# Ustaw użytkownika root do ewentualnej instalacji (np. pip)
USER root

# (Opcjonalnie) zainstaluj pip dependencies – jeśli potrzebujesz
# RUN pip install -r requirements.txt

# Wracamy na użytkownika Spark
USER 1001

# Uruchom aplikację Spark z konektorem Kafka
CMD ["/opt/bitnami/spark/bin/spark-submit", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1", \
     "--master", "local[*]", \
     "/app/main.py"]
