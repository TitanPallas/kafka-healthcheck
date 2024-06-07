# Get shell access to the kafka pod:

kubectl run my-kafka-client --restart='Never' --image docker.io/bitnami/kafka:3.7.0-debian-12-r6 --namespace CHANGEME --command -- sleep infinity 
kubectl exec --tty -i my-kafka-client --namespace CHANGEME -- bash

# Manual topic creation, from shell session inside the pod:
kafka-topics.sh --create --topic health_checks_topic --partitions 1 --replication-factor 1 --if-not-exists --command-config /tmp/client.properties --bootstrap-server my-kafka:9092
kafka-topics.sh --list --command-config /tmp/client.properties --bootstrap-server my-kafka:9092