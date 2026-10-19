class Espositore:
    def __init__(self, codice, nome, cognome):
        self._codice = codice
        self._nome = nome
        self._cognome = cognome
        self._stand_assegnato = None

    @property
    def codice(self):
        return self._codice

    @property
    def nome(self):
        return self._nome

    @property
    def cognome(self):
        return self._cognome

    @property
    def stand_assegnato(self):
        return self._stand_assegnato

    @stand_assegnato.setter
    def stand_assegnato(self, stand):
        self._stand_assegnato = stand

    def __eq__(self, other):
        if isinstance(other, Espositore):
            return self._codice == other._codice
        return False

    def __str__(self):
        desc = f"{self._codice} - {self._nome} {self._cognome}"
        if self._stand_assegnato is not None:
            desc += f" (Stand: {self._stand_assegnato.codice})"
        else:
            desc += " (Nessuno stand assegnato)"
        return desc


class Stand:
    def __init__(self, codice, superficie, padiglione, prezzo_base):
        self._codice = codice
        self._superficie = float(superficie)
        self._padiglione = padiglione
        self._prezzo_base = float(prezzo_base)
        self._espositore = None

    @property
    def codice(self):
        return self._codice

    @property
    def superficie(self):
        return self._superficie

    @property
    def padiglione(self):
        return self._padiglione

    @property
    def prezzo_base(self):
        return self._prezzo_base

    @property
    def espositore(self):
        return self._espositore

    @espositore.setter
    def espositore(self, espositore):
        self._espositore = espositore

    @property
    def disponibile(self):
        return self._espositore is None

    def calcola_prezzo(self):
        """Metodo polimorfico: per lo stand standard restituisce il prezzo base"""
        return self._prezzo_base

    def __eq__(self, other):
        if isinstance(other, Stand):
            return self._codice == other._codice
        return False

    def __lt__(self, other):
        """Confronta due stand in base al loro prezzo finale calcolato"""
        if isinstance(other, Stand):
            return self.calcola_prezzo() < other.calcola_prezzo()
        return NotImplemented

    def __str__(self):
        stato = "Disponibile" if self.disponibile else f"Assegnato a {self._espositore.codice}"
        return (f"{self._codice}: Standard | {self._superficie:g} mq - "
                f"Padiglione {self._padiglione} - Prezzo {self.calcola_prezzo():.2f}€ - {stato}")


class StandPreseExtra(Stand):
    def __init__(self, codice, superficie, padiglione, prezzo_base, prese_extra):
        super().__init__(codice, superficie, padiglione, prezzo_base)
        self._prese_extra = int(prese_extra)

    @property
    def prese_extra(self):
        return self._prese_extra

    def calcola_prezzo(self):
        # Sovrapprezzo del 7% per ogni presa extra
        return self._prezzo_base * (1 + 0.07 * self._prese_extra)

    def __str__(self):
        stato = "Disponibile" if self.disponibile else f"Assegnato a {self._espositore.codice}"
        return (f"{self._codice}: Prese Extra | {self._superficie:g} mq - "
                f"Padiglione {self._padiglione} - Prezzo {self.calcola_prezzo():.2f}€ - "
                f"Prese aggiuntive: {self._prese_extra} - {stato}")


class StandPremium(Stand):
    def __init__(self, codice, superficie, padiglione, prezzo_base, posizione):
        super().__init__(codice, superficie, padiglione, prezzo_base)
        self._posizione = posizione

    @property
    def posizione(self):
        return self._posizione

    def calcola_prezzo(self):
        # Sovrapprezzo fisso del 30%
        return self._prezzo_base * 1.30

    def __str__(self):
        stato = "Disponibile" if self.disponibile else f"Assegnato a {self._espositore.codice}"
        return (f"{self._codice}: Premium | {self._superficie:g} mq - "
                f"Padiglione {self._padiglione} - Posizione: {self._posizione} - "
                f"Prezzo {self.calcola_prezzo():.2f}€ - {stato}")


class LingottoFiere:
    def __init__(self, nome):
        """Inizializza gli attributi e le strutture dati"""
        self._nome = nome
        self._stand = {}         # dizionario codice_stand -> oggetto Stand
        self._espositori = {}    # dizionario codice_espositore -> oggetto Espositore

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, nuovo_nome):
        self._nome = nuovo_nome

    def carica_file_dati(self, file_path):
        """Carica i dati (stand ed espositori) dal file"""
        with open(file_path, mode="r", encoding="utf-8") as f:
            for riga in f:
                riga = riga.strip()
                if not riga:
                    continue

                parti = [p.strip() for p in riga.split(",")]

                # Se la riga descrive uno Stand (inizia per 'ST')
                if parti[0].startswith("ST"):
                    codice = parti[0]
                    superficie = parti[1]
                    padiglione = parti[2]
                    prezzo_base = parti[3]

                    if len(parti) == 4:
                        # Stand Standard
                        stand = Stand(codice, superficie, padiglione, prezzo_base)
                    elif len(parti) == 5:
                        valore_extra = parti[4]
                        # Se è un intero si tratta di prese extra, altrimenti Premium
                        if valore_extra.isdigit():
                            stand = StandPreseExtra(codice, superficie, padiglione, prezzo_base, int(valore_extra))
                        else:
                            stand = StandPremium(codice, superficie, padiglione, prezzo_base, valore_extra)
                    else:
                        continue

                    self._stand[codice] = stand

                # Se la riga descrive un Espositore (inizia per 'ES')
                elif parti[0].startswith("ES"):
                    if len(parti) >= 3:
                        codice = parti[0]
                        nome = parti[1]
                        cognome = parti[2]
                        self._espositori[codice] = Espositore(codice, nome, cognome)

    def assegna_stand_a_espositore(self, codice_stand, codice_espositore):
        """Associa uno stand a un espositore"""
        if codice_stand not in self._stand:
            raise ValueError(f"Lo stand {codice_stand} non esiste.")

        if codice_espositore not in self._espositori:
            raise ValueError(f"L'espositore {codice_espositore} non esiste.")

        stand = self._stand[codice_stand]
        espositore = self._espositori[codice_espositore]

        if not stand.disponibile:
            raise ValueError(f"Lo stand {codice_stand} è già occupato.")

        if espositore.stand_assegnato is not None:
            raise ValueError(f"L'espositore {codice_espositore} ha già uno stand assegnato ({espositore.stand_assegnato.codice}).")

        # Assegnazione reciproca
        stand.espositore = espositore
        espositore.stand_assegnato = stand

    def elenca_espositori(self):
        """Stampa l'elenco degli espositori mostrando, per ognuno, lo stand a cui è associato, quando applicabile"""
        if not self._espositori:
            print("Nessun espositore presente nel sistema.")
            return

        for espositore in self._espositori.values():
            print(espositore)

    def stand_ordinati_per_prezzo(self):
        """Restituisce la lista ordinata degli stand in base al prezzo"""
        # Sfrutta il metodo __lt__ definito nella classe Stand
        return sorted(self._stand.values())