
from locust import HttpUser, task, between


class TokoAlatTulisUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def lihat_semua_alat_tulis(self):
        self.client.get("/alat-tulis/")

    @task(2)
    def lihat_detail_alat_tulis(self):
        response = self.client.get("/alat-tulis/")

        if response.status_code == 200:
            data = response.json()

            if data:
                alat_tulis_id = data[0]["id"]

                self.client.get(
                    f"/alat-tulis/{alat_tulis_id}"
                )

    @task(1)
    def lihat_transaksi(self):
        self.client.get("/transactions/")
