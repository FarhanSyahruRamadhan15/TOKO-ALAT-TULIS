
from locust import HttpUser, task, between


class TokoAlatTulisUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def lihat_semua_alat_tulis(self):
        self.client.get("/alat-tulis/")

    @task(2)
    def lihat_detail_alat_tulis(self):
        self.client.get("/alat-tulis/1")

    @task(1)
    def lihat_transaksi(self):
        self.client.get("/transactions/")
