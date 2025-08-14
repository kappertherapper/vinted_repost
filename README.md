# Vinted Repost Script
8
Dette script automatiserer processen med at hente information om annoncer på vinted - gemmer billeder og data, samt sletter den gamle annonce.  

⚠️ **Bemærk:** Brug af automatiseringsværktøjer på Vinted kan være i strid med deres vilkår. Brug scriptet ansvarligt og på egen risiko.

---

## Funktioner

- Logger ind på Vinted via browser (manuelt login kræves).  
- Navigerer til din profil og finder den sidste aktive annonce.  
- Henter titel, pris, beskrivelse, detaljer og billeder fra annoncen.  
- Downloader billeder til en lokal `images`-mappe.  
- Gemmer annoncedata i en `vinted_data.json`-fil.  
- Kan slette den sidste annonce (valgfrit).  

---

## Krav

- Python 3.10+  
- [Selenium](https://pypi.org/project/selenium/)  
- [undetected-chromedriver](https://pypi.org/project/undetected-chromedriver/)  
- [Requests](https://pypi.org/project/requests/)  

Installer kravene via pip:

```bash
pip install selenium undetected-chromedriver requests