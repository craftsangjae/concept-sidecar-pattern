import click
import os
import subprocess
from kubernetes import client, config
import time

config.load_config()
core_api = client.CoreV1Api()


@click.command()
@click.argument("target_dir")
@click.argument("object_dir")
def upload_to_minio(target_dir: str, object_dir: str):
    job_name = os.getenv("JOB_NAME", '')
    namespace = os.getenv('NAMESPACE', '')

    bucket_name = os.getenv('BUCKET_NAME')

    endpoint_url = os.getenv("ENDPOINT_URL", '')
    access_key = os.getenv("ACCESS_KEY",'')
    secret_key = os.getenv("SECRET_KEY",'')

    # 이걸로 myminio 등록되었음
    print("before mc alias")
    subprocess.run(["mc", "alias", "set", "minio", endpoint_url, access_key, secret_key])
    print("after mc alias")

    # 파드 리스트 가져오기
    while True:
        print("Checking pod status...")
        time.sleep(1)
        pods = core_api.list_namespaced_pod(namespace, label_selector=f"job-name={job_name}")

        for pod in pods.items:
            print(f"Pod Name: {pod.metadata.name}")
            for container_status in pod.status.container_statuses:
                if container_status.name != 'main-container':
                    continue

                if container_status.ready:
                    print("Ready!")
                    subprocess.run(["mc", "mirror", target_dir, f"minio/{bucket_name}/{object_dir}"])
                elif container_status.state.terminated:
                    print("TERMINATED!")
                    if container_status.state.terminated.reason == 'Error':
                        print("ERROR!")
                        return
                    elif container_status.state.terminated.reason == 'Completed':
                        print("COMPLETED!")
                        subprocess.run(["mc", "mirror", target_dir, f"minio/{bucket_name}/{object_dir}"])
                        return




if __name__ == '__main__':
    upload_to_minio()
