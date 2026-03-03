# -*- coding: utf-8 -*-
import requests
import json
import time

def main():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'MediaHubMX/2',
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=utf-8'
    })
    
    try:
        # Carichiamo l'indice dei gruppi
        group_res = session.get("https://www2.vavoo.to/live2/index?output=json", timeout=20).json()
        # Filtriamo immediatamente solo il gruppo "Italy"
        search_groups = sorted(list(set([c.get("group") for c in group_res if c.get("group") == "Italy"])))
    except Exception as e:
        print(f"Errore durante il caricamento dei gruppi: {e}")
        return

    if not search_groups:
        print("Gruppo 'Italy' non trovato. Verifica la connessione o la sorgente.")
        return

    m3u_lines = ["#EXTM3U"]
    full_json_data = {}

    for country in search_groups:
        full_json_data[country] = []
        cursor = 0
        print(f"Lade Gruppe: {country}...", end="", flush=True)
        
        while True: 
            payload = {
                "language": "it", "region": "IT", "catalogId": "vto-iptv", "id": "vto-iptv",
                "adult": False, "search": "", "sort": "name", "filter": {"group": country},
                "cursor": cursor, "clientVersion": "3.0.2"
            }

            try:
                r = session.post("https://vavoo.to/vto-cluster/mediahubmx-catalog.json", 
                                 data=json.dumps(payload), timeout=30)
                
                if r.status_code == 200:
                    data = r.json()
                    items = data.get("items", [])
                    
                    for item in items:
                        name = item.get("name", "Unknown")
                        clean_name = name.split(".")[0].strip()
                        url = item.get("url", "")
                        
                        if url:
                            m3u_lines.append(f'#EXTINF:-1 group-title="{country}",{clean_name}')
                            m3u_lines.append(url)
                            full_json_data[country].append({"name": clean_name, "url": url, "group": country})
                    
                    cursor = data.get("nextCursor")
                    if not cursor:
                        break 
                else:
                    break
            except Exception:
                break
        
        print(f" Fertig ({len(full_json_data[country])} Kanäle)")
        time.sleep(0.05)

    # --- SALVATAGGIO SUI FILE ORIGINALI ---
    with open("vavoo_all.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines))
    
    with open("vavoo_full.json", "w", encoding="utf-8") as f:
        json.dump(full_json_data, f, ensure_ascii=False, indent=4)
        
    print("\nUpdate completato. I file vavoo_all e vavoo_full sono stati aggiornati (solo Italy).")

if __name__ == "__main__":
    main()
