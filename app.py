from flask import Flask, request, render_template
from minio import Minio
import io
import docker
import os

app = Flask(__name__)

MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')


@app.route("/", methods=["GET"])
def index():
    if request.args.get('MQTT IP'):
        mqtt = request.args.get('MQTT IP')
        msg_per_sec = float(request.args.get('msg per second'))
        msg_data = request.args.get('message data')
        checkbox = request.args.get('alt-data')
        alt_msg_data = request.args.get('alt message data')

        mqtt_config = str({'mqtt_ip': mqtt,
                           'msg_per_sec': msg_per_sec,
                           'msg_data': msg_data,
                           'checkbox': checkbox,
                           'alt_msg_data': alt_msg_data})

        minioClient = Minio('minio:9000',
                            access_key=MINIO_ACCESS_KEY,
                            secret_key=MINIO_SECRET_KEY,
                            secure=False)

        mqtt_conf_io = io.BytesIO(mqtt_config.encode())
        io_len = len(mqtt_config)

        try:
            minioClient.put_object("mqtt", "mqtt_config.json", mqtt_conf_io, io_len)
        except ResponseError as err:
            minioClient.make_bucket("mqtt")
            minioClient.put_object("mqtt", "mqtt_config.json", mqtt_conf_io, io_len)

        try:
            docker_client.services.create("ciscodevnet/mqtt_forward:latest",
                                          name="mqtt_forward",
                                          networks=["mqtt_datasvc"])
        except BaseException:
            mqtt_fwd_service = docker_client.services.get("mqtt_forward")
            mqtt_fwd_service.remove()
            docker_client.services.create("ciscodevnet/mqtt_forward:latest",
                                          name="mqtt_forward",
                                          networks=["mqtt_datasvc"])

        return render_template("index.html")
    else:
        return render_template("index.html")

    # return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5656, debug=True)
