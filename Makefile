app_name = kck-flask
app_version = 0.1.0
app=$(app_name):$(app_version)


build:
	@docker build -t $(app) .

run:
	docker run -v ${PWD}/client_secrets.json:/app/client_secrets.json --rm --detach -p 8080:8080 $(app)

kill:
	@echo 'Killing container $(app)'
	@docker ps | grep $(app_name) | awk '{print $$1}' | xargs docker stop
