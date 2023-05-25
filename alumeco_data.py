import sqlite3
import random

class Order():
    def __init__(self, vare, pris, kunde, status, order_id,x,  y):
        self.vare = vare
        self.pris = pris
        self.kunde = kunde
        self.status = status
        self.order_id = order_id

    
    def setId(self, id):
        self.order_id = id
class AlumecoData():

    def __init__(self):
        self.db = sqlite3.connect("alumecodata.db")

        #self.create_tables()
        #self.create_data()

    def get_random_vare_id(self):
        c = self.db.cursor()
        c.execute('''
            SELECT id FROM Varer ORDER BY RANDOM() LIMIT 1;
        ''')        
        return c.fetchone()[0]
    
    def get_random_kunde_id(self):
        c = self.db.cursor()
        c.execute('''
            SELECT id FROM Kunder ORDER BY RANDOM() LIMIT 1;
        ''')
        a = c.fetchone()[0]     
        return a

    def get_list(self):
        c = self.db.cursor()
        c.execute('''
        SELECT vm.navn, GROUP_CONCAT(vm.pris), om.id, om.kunde_id, om.status, ov.antal, ll.x, ll.y 
        FROM Ordrer om 
        INNER JOIN OrdreVarer ov 
        ON om.id = ov.ordre_id 
        INNER JOIN Varer vm 
        ON ov.vare_id = vm.id INNER JOIN LagerLokationer ll
        GROUP BY om.id 
        ''')
        o_liste = []
        for v in c:
            ordre = Order(v[0], v[1], v[3], v[4], v[2],v[5],v[6])
            #ordre.setId(v[2])
            o_liste.append(ordre)
        return o_liste
    
    def get_vare_til_ordre(self,order_id,vare_id):
        c = self.db.cursor()
        id = order_id

        print(" Finder vare til ordre:{}".format(order_id))
        c.execute('''
        SELECT v.vare_id, v.antal, l.vare_id FROM OrdreVarer v INNER JOIN LagerLokationer l WHERE v.ordre_id = ? WHERE l.vare_id = ?

        ''',[order_id], [vare_id])

        c3 = self.db.cursor()
        SamletPris = []
        for vare in c:
            c3.execute('''
            SELECT v.navn, v.pris, v.id, l.x, l.y FROM Varer v INNER JOIN LagerLokationer l WHERE v.id = ? WHERE l.vare_id = ?''',[vare[0]],[vare_id[0]])

            result = c3.fetchone()
            if result is not None:
                a = result[0]
                b = result[1]
                c = result[2]
                d = result[3]
                e = result[4]
            
                SamletPris.append(float(b))
                print("{} Pris: {} kr (id: {}). Lokationen på varen er: (X:{},Y:{})".format(a,b,c,d,e))

            else:
                print("Ingen opslag fundet for vare_id: {}".format(vare[0]))

        print(" Værdi af ordre {}".format(sum(SamletPris)))

    def calculateTotalPrice(self, order_id):
        c = self.db.cursor()
        id = order_id

        print(" Finder vare til ordre:{}".format(order_id))
        c.execute('''
        SELECT vare_id, antal FROM OrdreVarer WHERE ordre_id = ?

        ''',[order_id])

        c3 = self.db.cursor()
        SamletPris = []
        for vare in c:
            c3.execute('''
            SELECT navn, pris, id FROM Varer WHERE id = ?''',[vare[0]])

            result = c3.fetchone()
            if result is not None:
                b = result[1]
            
                SamletPris.append(float(b))
            else:
                print("Ingen opslag fundet for vare_id: {}".format(vare[0]))
        return(sum(SamletPris))
    

    def create_data(self):
        c = self.db.cursor()

        ## Opret Varer
        varenavne = ['Alu ', 'Jern ', 'Messing ', 'Kobber ', 'Stål ']
        varetyper = ['pind ', 'stang ', 'rør ', 'skrue ', 'kasse ', 'beslag ', 'dims ', 'møtrik ', 'bolt ']
        varestørrelser = [' 1x1 ', ' 2x2 ', '3x3 ', ' 5x5 ', '10x10 ', '20x20 ', ' 50x50 ', ' 100x100 ', ' 200x200 ']        
        for navn in varenavne:
            for type in varetyper:
                for størrelse in varestørrelser:
                    varenavn = navn + type + størrelse
                    c.execute('''
                        INSERT INTO Varer (navn, pris) VALUES (?,?);
                    ''', [varenavn, random.random() * 1000])

        ## Opret lagerlokationer. Nogle lokationer efterlades tomme.
        for x in range(63):     # x rækker
            for y in range(9): # med y hylder på hver række
                if random.random() < 0.99:
                    vare_id = self.get_random_vare_id()
                else:
                    vare_id = None
                c.execute('''
                    INSERT INTO Lagerlokationer (x,y,vare_id,antal) VALUES (?,?,?,?);
                ''', [x,y,vare_id, random.randint(1,10)])

        ## Opret kunder
        kundenavne = ['Alu', 'Jern', 'Maskin', 'Messing', 'Kobber', 'Stål']
        kundetyper = ['Eksperten', 'Imperiet', 'Handelen', 'Butikken', 'Tilbud', 'Innovation', 'Giganten']
        
        for i in range(300):            
            navn = random.choice(kundenavne) + random.choice(kundetyper) + f' {random.randint(1,100)}'
            c.execute('''
                INSERT INTO Kunder (navn, prioritet) VALUES (?,?);
            ''', [navn, random.randint(1,3)])        

        ## Opret Ordrer
        for i in range(100):
            kunde_id = self.get_random_kunde_id()
            print(f"Opretter ordre til: {kunde_id}")
            c.execute('''
                INSERT INTO Ordrer (kunde_id, status) VALUES (?,0);
            ''', [kunde_id])

        ## Tilføj Varer til Ordrer
        c.execute('SELECT id FROM Ordrer;')
        c2 = self.db.cursor()
        for ordre in c:
            print(f"Tilføjer varer til ordre {ordre[0]}")
            for vare in range(random.randint(1,10)):
                antal = random.randint(1,10)
                vare_id = self.get_random_vare_id()
                c2.execute('''
                    INSERT INTO OrdreVarer (ordre_id, vare_id, antal) VALUES (?,?,?);
                ''', [ordre[0], vare_id, antal])



        self.db.commit()


    def create_tables(self):
        c = self.db.cursor()

        try:
            c.execute('''
                CREATE TABLE Ordrer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
		            kunde_id INTEGER,
                    status INTEGER);
            ''')
        except:
            print("Tabellen findes allerede")

        try:
            c.execute('''
                CREATE TABLE OrdreVarer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
		            ordre_id INTEGER,
                    vare_id INTEGER,
                    antal INTEGER);
            ''')
        except:
            print("Tabellen findes allerede")

        try:
            c.execute('''
                CREATE TABLE Varer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    navn TEXT,
		            pris FLOAT);
            ''')
        except:
            print("Tabellen findes allerede")

        try:
            c.execute('''
                CREATE TABLE Kunder (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
		            navn TEXT,
                    prioritet INTEGER);
            ''')
        except:
            print("Tabellen findes allerede")
        
        try:
            c.execute('''
                CREATE TABLE LagerLokationer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
		            x INTEGER,
                    y INTEGER,
                    vare_id INTEGER,
                    antal INTEGER);
            ''')
        except:
            print("Tabellen findes allerede")

        self.db.commit()


data = AlumecoData()

# data.get_vare_til_ordre(random.randint(1,100),)