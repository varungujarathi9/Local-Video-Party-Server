from server_rest import app, socketIo

# do some production specific things to the app
app.debug = False
socketIo.run(app)