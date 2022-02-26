run:
	waitress-serve --port 80 --no-expose-tracebacks --call 'app:create_app'
