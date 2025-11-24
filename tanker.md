API Informationen
Die Tankerkönig-API besteht aus drei HTTP-GET-Methoden, um Tankstellen-Informationen und Preise zu holen, sowie einer HTTP-POST-Methode, mit der fehlerhafte Daten an die MTS-K gemeldet werden können.

Die API kann von einem Server (z.B. über PHP), vom Browser (via JavaScript/AJAX) oder auch per Direktaufruf der URL (ideal zum Testen) abgefragt werden. Als Datenformat wird JSON zurückgeliefert.

Demo-Key
Die Beispielaufrufe hier werden mit dem Demo-Key gemacht. Im Unterschied zu echten Keys werden keine echten Preise ausgeliefert. Außerdem sind die Daten zur besseren Lesbarkeit formatiert.

Requests allgemein
In jedem Aufruf einer API-Methode muss ein API-Key mit angegeben werden.
Die Antwort enthält immer ein ok flag, dessen Status abgefragt werden sollte. Im Fehlerfall (ok == false) enthält die Antwort einen Text mit der Fehlerursache, bspw:
{
  "ok":false,
  "message":"parameter error"
}
Es ist sinnvoll und dringend empfohlen, immer das ok-Flag abzufragen um zu testen, ob der Aufruf erfolgreich war.
Je nach Applikation sollte der Fehler entsprechend behandelt werden, etwa so:
Fehlertext anzeigen,
Fehlertext an Server melden, falls ein eigener Server eingesetzt wird,
Keine weiteren Requests mehr senden
API-Methode 1 - Umkreissuche
Die Umkreissuche erfolgt über die API-Methode list.php. Damit können um einen gegebenen Standort die Tankstellen-Informationen und Preise der im angegebenen Radius befindlichen Tankstellen abgerufen werden.

Die Parameter dieses Request sind:

Parameter	Bedeutung	Format
lat	geographische Breite des Standortes	Floatingpoint-Zahl
lng	geographische Länge	Floatingpoint-Zahl
rad	Suchradius in km	Floatingpoint-Zahl, max: 25
type	Spritsorte	'e5', 'e10', 'diesel' oder 'all'
sort	Sortierung	price, dist (1)
apikey	Der persönliche API-Key	UUID
(1) Bei type=all wird immer nach Entfernung sortiert - die Angabe der Sortierung ist dann optional

Beispielaufruf
https://creativecommons.tankerkoenig.de/json/list.php?lat=52.521&lng=13.438&rad=1.5&sort=dist&type=all&apikey=00000000-0000-0000-0000-000000000002
Beispielantwort
{
    "ok": true,
    "license": "CC BY 4.0 -  https:\/\/creativecommons.tankerkoenig.de",
    "data": "MTS-K",
    "status": "ok",
    "stations": [
        {                                                     Datentyp, Bedeutung
            "id": "474e5046-deaf-4f9b-9a32-9797b778f047",   - UUID, eindeutige Tankstellen-ID
            "name": "TOTAL BERLIN",                         - String, Name
            "brand": "TOTAL",                               - String, Marke
            "street": "MARGARETE-SOMMER-STR.",              - String, Straße
            "place": "BERLIN",                              - String, Ort
            "lat": 52.53083,                                - float, geographische Breite
            "lng": 13.440946,                               - float, geographische Länge
            "dist": 1.1,                                    - float, Entfernung zum Suchstandort in km
            "diesel": 1.109,                                \
            "e5": 1.339,                                     - float, Spritpreise in Euro
            "e10": 1.319,                                   /
            "isOpen": true,                                 - boolean, true, wenn die Tanke zum Zeitpunkt der
                                                              Abfrage offen hat, sonst false
            "houseNumber": "2",                             - String, Hausnummer
            "postCode": 10407                               - integer, PLZ
        },
        ... weitere Tankstellen
    ]
}
                    
Alle Tankstelleninformation wie vom Betreiber angegeben.

Wenn nur eine Spritsorte abgefragt wird ist im JSON statt Name der Sorte 'price' angegeben.

Beispielcode
 

API-Methode 2 - Preisabfrage
Die Preisabfrage erfolgt über die API-Methode prices.php. Damit können die Preise von bis zu 10 bekannten Tankstellen gleichzeitig abgefragt werden.

Die Parameter dieses Request sind die IDs der entsprechenden Tankstellen:

Parameter	Bedeutung	Format
ids	IDs der Tankstellen	UUIDs, durch Komma getrennt
apikey	Der persönliche API-Key	UUID
Beispielaufruf
https://creativecommons.tankerkoenig.de/json/prices.php?ids=4429a7d9-fb2d-4c29-8cfe-2ca90323f9f8,446bdcf5-9f75-47fc-9cfa-2c3d6fda1c3b,60c0eefa-d2a8-4f5c-82cc-b5244ecae955,44444444-4444-4444-4444-444444444444&apikey=00000000-0000-0000-0000-000000000002
Beispielantwort
{
    "ok": true,
    "license": "CC BY 4.0 -  https:\/\/creativecommons.tankerkoenig.de",
    "data": "MTS-K",
    "prices": {
        "60c0eefa-d2a8-4f5c-82cc-b5244ecae955": {
            "status": "open",                               - Tankstelle ist offen
            "e5": false,                                    - kein Super
            "e10": false,                                   - kein E10
            "diesel": 1.189                                 - Tankstelle führt nur Diesel
        },
        "446bdcf5-9f75-47fc-9cfa-2c3d6fda1c3b": {
            "status": "closed"                              - Tankstelle ist zu
        },
        "4429a7d9-fb2d-4c29-8cfe-2ca90323f9f8": {
            "status": "open",
            "e5": 1.409,
            "e10": 1.389,
            "diesel": 1.129
        },
        "44444444-4444-4444-4444-444444444444": {
            "status": "no prices"                           - keine Preise für Tankstelle verfügbar
        }
    }
}
                    
Beispielcode

API-Methode 3 - Detailabfrage
Mit der Detail-Abfrage werden einige wenige Informationen geliefert, die in der Antwort der Umkreissuche nicht enthalten sind: detail.php.

Parameter-Name	Bedeutung	Werte
openingTimes	Öffnungszeiten	Array mit Objekten, in denen der Text und die Zeiten stehen
overrides	erweiterte Öffnungszeiten	Änderungen der regulären ÖZ - bspw. eine temporäre Schliessung
wholeDay	ganztägig geöffnet	true, false
state	Bundesland	Ein Kürzel für das Bundesland - ist meist nicht angegeben
Ein Aufruf dieser Funktion ist für Apps sinnvoll, wenn dem User Details einer ausgewählten Tankstelle angezeigt werden sollen.
Zur regelmäßigen Preisabfragen ist diese Methode nicht gedacht. Statt dessen sollte hier die Umkreissuche, oder die Preisabfrage verwendet werden.

Die Parameter dieses Request sind neben dem API-Key die ID der Tankstelle:

Parameter	Bedeutung	Format
id	ID der Tankstelle	UUID
apikey	Der persönliche API-Key	UUID
Beispielaufruf
https://creativecommons.tankerkoenig.de/json/detail.php?id=24a381e3-0d72-416d-bfd8-b2f65f6e5802&apikey=00000000-0000-0000-0000-000000000002
Beispielantwort
Eine Tankstelle mit geänderten Öffnungszeiten:
{
    "ok": true,
    "license": "CC BY 4.0 -  https:\/\/creativecommons.tankerkoenig.de",
    "data": "MTS-K",
    "status": "ok",
    "station": {
        "id": "24a381e3-0d72-416d-bfd8-b2f65f6e5802",
        "name": "Esso Tankstelle",
        "brand": "ESSO",
        "street": "HAUPTSTR. 7",
        "houseNumber": " ",
        "postCode": 84152,
        "place": "MENGKOFEN",
        "openingTimes": [                                               - Array mit regulären Öffnungszeiten
            {
                "text": "Mo-Fr",
                "start": "06:00:00",
                "end": "22:30:00"
            },
            {
                "text": "Samstag",
                "start": "07:00:00",
                "end": "22:00:00"
            },
            {
                "text": "Sonntag",
                "start": "08:00:00",
                "end": "22:00:00"
            }
        ],
        "overrides": [                                                  - Array mit geänderten Öffnungszeiten
            "13.04.2017, 15:00:00 - 13.11.2017, 15:00:00: geschlossen"  - im angegebenen Zeitraum geschlossen
        ],
        "wholeDay": false,                                              - nicht ganztägig geöffnet
        "isOpen": false,
        "e5": 1.379,
        "e10": 1.359,
        "diesel": 1.169,
        "lat": 48.72210601,
        "lng": 12.44438439,
        "state": null                                                   - Bundesland nicht angegeben
    }
}                        
Beispielcode

API-Methode 4 - Fehlermeldung
Über die API können mit complaint.php auch fehlerhafte Daten über uns an die MTS-K weitergeleitet werden.

Die Parameter dieses Request sind wie folgt:

Parameter	Bedeutung	Format
id	ID der Tankstelle	UUID
apikey	Der persönliche API-Key	UUID
type	Fehlertyp	(2)
correction	korrigierter Wert	
ts	Timestamp	Unix-Sekunden
Optionale Angabe, wird die Timestamp nicht gesetzt wird die aktuelle Zeit genommen
(2) Liste der Fehlertypen

Fehlertyp	Bedeutung
wrongPetrolStationName	Der Name entspricht nicht der Angabe. Korrektur: richtiger Name.
wrongStatusOpen	Die Tankstelle ist offen, obwohl sie laut Öffnungszeitenangabe zu sein sollte.
correction wird nicht angegeben.
wrongStatusClosed	Die Tankstelle ist zu, obwohl sie laut Öffnungszeitenangabe offen sein sollte.
correction wird nicht angegeben.
wrongPriceE5	Falscher Super-Preis. Korrektur: Gleitpunktzahl mit korrektem Wert.
wrongPriceE10	Falscher E10-Preis. Korrektur: Gleitpunktzahl mit korrektem Wert.
wrongPriceDiesel	Falscher Diesel-Preis. Korrektur: Gleitpunktzahl mit korrektem Wert.
wrongPetrolStationBrand	Marke stimmt nicht. Korrektur: Angabe des richtigen Namens.
wrongPetrolStationStreet	Straßenname stimmt nicht. Korrektur: Angabe des richtigen Namens.
wrongPetrolStationHouseNumber	Hausnummer stimmt nicht. Korrektur: Angabe der richtigen Hausnummer.
wrongPetrolStationPostcode	PLZ stimmt nicht. Korrektur: Angabe der richtigen PLZ.
wrongPetrolStationPlace	Ortsname stimmt nicht. Korrektur: Angabe der richtiger Ortsname.
wrongPetrolStationLocation	Geokoordinaten stimmen nicht. Korrektur: Angabe der richtigen Koordinaten.
Format: 2 mit Komma getrennte Gleitpunktzahlen für geographische Breite und Länge.
Es sind ausschliesslich die angegeben Meldungstypen erlaubt
Es sind ausschliesslich Korrekturen erlaubt - keine Anmerkungen
Mit einer Meldung kann nur ein Fehler gemeldet werden
Es wird nur eine syntaktische Prüfung durchgeführt, keine inhaltliche
Die Daten werden an die MTS-K weitergegeben, die sie an die Tankstellenbetreiber weitergibt
Tankerkönig ist hier nur der Vermittler der Daten
Beispielcode

Beispiel-Meldungs-Aufrufe mit jQuery
function sendComplaint(stationId, complaintType, correction){
    var apikey = '00000000-0000-0000-0000-000000000002'; // Demo-Key nur zum Testen, diese Requests werden nicht weitergegeben

    var data = {
        apikey: apikey,
        id: stationId,
        type: complaintType
    };

    if (correction) {
        data.correction = correction;
    }

    $.ajax({
        url: "https://creativecommons.tankerkoenig.de/json/complaint.php",
        method: 'POST',
        data: data,
        success: function( response ) {
            if (!response.ok) {
                alert(response.message);
            } else {
                alert('Meldung erfolgreich übertragen');
            }
        }
    });
}

var stationId = 'd3f68a43-e249-4a1f-bd34-0023677cdcc9';

// Test 1
sendComplaint(stationId, 'wrongStatusClosed', null);    // keine Korrekturangabe erlaubt

// Test 2
sendComplaint(stationId, 'wrongPriceDiesel', 1.234);

// Test 3
sendComplaint(stationId, 'wrongPetrolStationLocation', '52.29162,10.06117');

// Test 4
sendComplaint(stationId, 'illegal token', '52.29162,10.06117');
                    
Die ersten 3 Aufrufe sind korrekt, die Antwort ist:

{
    "ok": true
}
                    
Der letzte Aufruf ist fehlerhaft, die Antwort ist:

{
    "ok": false,
    "message": "Meldungstyp 'illegal token' nicht erlaubt"
}
                    