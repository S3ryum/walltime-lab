# walltime-lab

IANA saat dilimi verisindeki saat değişimlerinde yerel saatte hangi aralığın atlandığını veya iki kez yaşandığını bulan Python kütüphanesi ve CLI.

~~~sh
python -m pip install .
walltime-lab Europe/Amsterdam 2026
walltime-lab America/New_York 2026 --json
~~~

Harici servis kullanmaz; kurulu IANA verisini okur. Windows ve sisteminde saat dilimi verisi bulunmayan ortamlar için tzdata ek paketini kur: python -m pip install ".[tzdata]". Ayrıntılar için [İngilizce README](README.md) ve [tasarım belgesi](docs/DESIGN.md).
