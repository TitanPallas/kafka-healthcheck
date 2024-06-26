# Install Prometheus by following these instructions:
## Add the Helm Repository for Prometheus:
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```
## Deploy the Prometheus Helm Chart with the prometheus-values.yml.
```
helm install prometheus -f ./chart-values/prometheus-values.yml prometheus-community/kube-prometheus-stack
```

# Install Kafka by following these instructions:

## Add the Helm Repository for Kafka:
```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

## Deploy the Kafka Helm Chart with the values.yaml. The topic is also going to be created automatically:
```
helm install my-kafka -f ./chart-values/kafka-values.yml bitnami/kafka 
```

## Alternatively you can use your own set of values.yml, but you need to rebuild the Docker images.
```
helm install my-kafka bitnami/kafka --set fullnameOverride=my-kafka
```

## To connect a client to your Kafka, you need to create the 'client.properties' configuration files with the content below:
```
security.protocol=SASL_PLAINTEXT
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
    username="user1" \
    password="$(kubectl get secret my-kafka-user-passwords --namespace CHANGEME -o jsonpath='{.data.client-passwords}' | base64 -d | cut -d , -f 1)";
```

## To create a pod that you can use as a Kafka client you run the following commands:
```
kubectl run my-kafka-client --restart='Never' --image docker.io/bitnami/kafka:3.7.0-debian-12-r6 --namespace CHANGEME --command -- sleep infinity 
kubectl exec --tty -i my-kafka-client --namespace CHANGEME -- bash
kafka-topics.sh --create --topic health_checks_topic --partitions 1 --replication-factor 1 --if-not-exists --command-config /tmp/client.properties --bootstrap-server my-kafka:9092
kafka-topics.sh --list --command-config /tmp/client.properties --bootstrap-server my-kafka:9092
```

