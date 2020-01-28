curl -X PUT "localhost:9200/_cluster/settings" -H 'Content-Type: application/json' -d'
{
  "transient": {
    "cluster.routing.allocation.disk.watermark.low": "30mb",
    "cluster.routing.allocation.disk.watermark.high": "20mb",
    "cluster.routing.allocation.disk.watermark.flood_stage": "10mb",
    "cluster.info.update.interval": "1m"
  }
}
'
curl -XPUT -H "Content-Type: application/json" http://localhost:9200/_all/_settings -d '{"index.blocks.read_only_allow_delete": null}'
curl -XPUT "http://localhost:9200/_cluster/settings" -d'
{
  "persistent": {
    "cluster": {
      "routing": {
        "allocation.disk.threshold_enabled": false
      }
    }
  }
}'
