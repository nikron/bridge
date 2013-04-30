curl -v -H "Content-Type: application/json; charset=utf-8" -X POST -d '{"name" : "Test", "service" : "insteon", "asset class" : "ApplianceLinc V2", "real id" : "00f1d1"}' localhost:8080/assets
curl localhost:8080/assets
curl -v -H "Content-Type: application/json; charset=utf-8" -X POST -d '{ "save" : "default.bridge" }' localhost:8080
