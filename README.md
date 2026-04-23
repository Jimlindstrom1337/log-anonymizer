# Log Anonymizer

Ersätter känslig data i loggar med realistisk mock-data — körs helt lokalt, ingen data lämnar din maskin.

**Detekterar och ersätter:**
- Personnummer (svenska format)
- E-postadresser
- Telefonnummer
- IP-adresser (IPv4 och IPv6)

Samma värde → samma ersättning inom en session (konsistent anonymisering).

## Kom igång

```bash
pip install -r requirements.txt
streamlit run app.py
```

Öppnas automatiskt på `http://localhost:8501`.
