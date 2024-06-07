# kafka-healthcheck
Install Kafka by following these instructions:

Add the Helm Repository for Kafka:
'''
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
'''

Deploy the Kafka Helm Chart:

Install Kafka using the Helm chart. Customize the values as needed.
helm install my-kafka bitnami/kafka --set fullnameOverride=my-kafka 

To connect a client to your Kafka, you need to create the 'client.properties' configuration files with the content below:
'''
security.protocol=SASL_PLAINTEXT
sasl.mechanism=SCRAM-SHA-256
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required \
    username="user1" \
    password="$(kubectl get secret my-kafka-user-passwords --namespace radu-deployment-strategies-2 -o jsonpath='{.data.client-passwords}' | base64 -d | cut -d , -f 1)";
'''

To create a pod that you can use as a Kafka client you run the following commands:
'''
kubectl run my-kafka-client --restart='Never' --image docker.io/bitnami/kafka:3.7.0-debian-12-r6 --namespace radu-deployment-strategies-2 --command -- sleep infinity 
kubectl exec --tty -i my-kafka-client --namespace radu-deployment-strategies-2 -- bash
kafka-topics.sh --create --topic health_checks_topic --partitions 1 --replication-factor 1 --if-not-exists --command-config /tmp/client.properties --bootstrap-server my-kafka:9092
kafka-topics.sh --list --command-config /tmp/client.properties --bootstrap-server my-kafka:9092
'''
or use the values.yaml with your own helm chart.