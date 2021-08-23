# Geotrashing
#### Projekt pro optimalizaci sběru odpadu
Myšlenka GeoTrashingu (https://geotrashing.opendatalab.cz/ ) vznikl na podzim roku 2019 na hackathonu NKU a autory jsou Tomáš Karella, Vlado Vancák a Nikita Tishin. V dnešní době existuje řešení na sledování zaplněnosti tříděných odpadových nádob, ale senzory jsou drahé a není možné je umístit všude. Nálepka s QR kódem nestojí moc a je možné ji nalepit takřka kamkoliv. Cílem je tedy nikoliv nahrazovat, ale doplňovat senzory tam, kde to nedává ekonomický smysl.

Od začátku bylo rozhodnuto, že aplikace musí běžet striktně na webu – jakákoliv instalace aplikací je pro uživatele krajně nepřívětivá a v případě cizinců může být i obtížná. Každý QR kód tak obsahuje unikátní ID, ke kterému je v databázi připojena informace o poloze typu apod.

### Spuštění
#### Prerekvizity
* [Docker](https://docs.docker.com/desktop)
#### Nastavení
* V .env nastavte příslušné názvy a hesla. 
* HOST_PORT a HOST_IP - je adresa v rámci dockeru 
* HOME_URL - je adresa na které bude web dostupný z venku 
#### Spuštění
```docker-compose up```
#### Přesměrování přes ngix
* Nastavte přesměrování na web běžící uvnitř Dockeru
* Příklad pro NGINX
```server {
   server_name geothrashing.opendatalab.cz;
   client_max_body_size 1M;


    location / {
      proxy_pass  http://localhost:5000;
    }
   }
```

### Webová stránka
Na webu naleznete základní informace o našem projektu, kontakty, webovou QR čtečku a interaktivní mapu, kde černé tečky reprezentují jednotlivé kontejnery (po kliknutí se zobrazí souhrné informace o hlášení plných košů)

Pro hlášení plného koše slouží url <URL>/full/<CisloKose>, na tuto stránku by měl přesměrovávat QR kód nalepený na kontejnerech. 

Pokud <CisloKose> ještě není v databázi, tak vám po naskenování web navrhne jej tam přidat. Bude však vyžadovat jméno a heslo definované v .env souboru (USER_NAME, USER_PASSWORD). 


### QR kódy
* Utilitka pro generování QR kódů je popsaná v podsložce [qr_generator](./qr_generator/README.md). 
