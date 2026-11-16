import sys
import time
import ssl
import urllib.request


def human_bytes(n: int) -> str:
	for unit in ("B", "KB", "MB", "GB"):
		if n < 1024 or unit == "GB":
			return f"{n:.2f} {unit}"
		n /= 1024
	return f"{n:.2f} GB"


def fetch_once(url):
	# Создаём SSL-контекст, используя свежие сертификаты от certifi
	ctx = ssl.create_default_context(cafile=certifi.where())
	
	req = urllib.request.Request(
		url,
		headers={"User-Agent": "speed-bench/1.0", "Accept-Encoding": "identity"},
	)
	start = time.perf_counter()
	total = 0
	# Передаём context в urlopen
	with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
		while True:
			chunk = resp.read(64 * 1024)
			if not chunk:
				break
			total += len(chunk)
	return time.perf_counter() - start, total


def main() -> int:
	if len(sys.argv) != 2:
		print(f"Usage: {sys.argv[0]} <URL>", file=sys.stderr)
		return 1

	url = sys.argv[1]
	RUNS = 10

	print(f"URL: {url}")
	print(f"Запросов: {RUNS}\n")

	times: list[float] = []
	total_bytes = 0

	for i in range(1, RUNS + 1):
		try:
			elapsed, size = fetch_once(url)
		except Exception as e:
			print(f"[{i:2d}] ОШИБКА: {e}", file=sys.stderr)
			return 2
		times.append(elapsed)
		total_bytes += size
		mbps = size / elapsed / (1024 * 1024) if elapsed > 0 else 0.0
		print(
			f"[{i:2d}] {elapsed:7.3f} c | {human_bytes(size):>12} | "
			f"{mbps:8.3f} МБ/с"
		)
		if i < RUNS:
			time.sleep(1.0)

	total_time = sum(times)
	avg_time = total_time / RUNS
	overall_mbps = total_bytes / total_time / (1024 * 1024) if total_time > 0 else 0.0
	
	avg_size = total_bytes / RUNS
	avg_mbps = avg_size / avg_time / (1024 * 1024) if avg_time > 0 else 0.0

	print("\n--- ИТОГИ ---")
	print(f"Среднее время запроса : {avg_time:.3f} c")
	print(f"Всего скачано        : {human_bytes(total_bytes)}")
	print(f"Средний размер ответа: {human_bytes(avg_size)}")
	print(f"Средняя скорость     : {avg_mbps:.3f} МБ/с (по среднему запросу)")
	print(f"Общая скорость       : {overall_mbps:.3f} МБ/с (весь объём / всё время)")
	return 0


if __name__ == "__main__":
	sys.exit(main())