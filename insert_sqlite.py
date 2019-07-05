import sqlite3

conn = sqlite3.connect("map.db")
c = conn.cursor()

card_id = [
  ("41 205 254 41" , 'NW'),
  ("252 94 249 41" , 'NE'),
  ("227 134 166 137" , 'SE'),
  ("47 34 231 89" , 'SW'),
  ("140 88 228 137" , 'N1'),
  ("158 220 186 89" , 'N2'),
  ("220 24 232 137" , 'N3'),
  ("119 44 171 169" , 'N4'),
  ("193 125 198 89" , 'N5'),
  ("014 137 254 41" , 'N6'),
  ("81 127 227 137" , 'N7'),
  ("186 134 166 137" , 'S1'),
  ("78 95 166 137" , 'S2'),
  ("255 014 167 137" , 'S3'),
  ("217 117 197 89" , 'S4'),
  ("137 40 167 137" , 'S5'),
  ("01 180 166 137" , 'S6'),
  ("50 74 227 41" , 'S7'),
  ("27 06 231 89" , 'W1'),
  ("01 84 254 41" , 'W2'),
  ("86 013 231 89" , 'W3'),
  ("187 205 166 137" , 'W4'),
  ("243 223 166 137" , 'B1'),
  ("43 180 230 89" , 'B2'),
  ("206 93 226 41" , 'B3'),
  ("218 125 230 89" , 'B4'),
  ("95 173 230 89" , 'B5'),
  ("128 03 231 89" , 'B6'),
  ("250 68 255 41" , 'B7'),
  ("127 240 92 41" , 'E1'),
  ("143 121 02 41" , 'E2'),
  ("143 99 01 41" , 'E3'),
  ("143 133 87 41" , 'E4'),
  ("143 05 104 41" , 'C1'),
  ("158 224 83 32" , 'C2'),
  ("57 156 167 137" , 'UB'),
  ("158 246 166 32" , 'C3'),
  ("143 101 015 41" , 'C4'),
  ("143 76 98 41" , 'EXTRA1'),
  ("143 78 107 41" , 'EXTRA2')
]

items = [
  ("NW" , "W1"),
  ("W1" , "W2"),
  ("W2" , "W3"),
  ("W3" , "W4"),
  ("W4" , "SW"),
  ("SW" , "S1"),
  ("S1" , "S2"),
  ("S2" , "S3"),
  ("S3" , "C4"),
  ("C4" , "C3"),
  ("C3" , "UB"),
  ("UB" , "C2"),
  ("C2" , "C1"),
  ("C1" , "N3,N5"),
  ("N3" , "N2"),
  ("N2" , "N1"),
  ("N1" , "NW"),
  ("N5" , "N6"),
  ("N6" , "N7"),
  ("N7" , "NE"),
  ("NE" , "E1"),
  ("E1" , "E2"),
  ("E2" , "B7,E3"),
  ("B7" , "B6"),
  ("B6" , "B5"),
  ("B5" , "B4"),
  ("B4" , "B3"),
  ("B3" , "B2"),
  ("B2" , "B1"),
  ("B1" , "W3"),
  ("E3" , "E4"),
  ("E4" , "SE"),
  ("SE" , "S7"),
  ("S7" , "S6"),
  ("S6" , "S5"),
  ("S5" , "C4") 
]

turns = [
  ("S3C4", "turn_left"),
  ("C1N3", "turn_left"),
  ("C1N5", "turn_right"),
  ("S5C4", "turn_right"),
  ("E2E3", "go_straight"),
  ("E2B7", "turn_right")
]

traffic_light_dict = [
  ("01 84 254 41", "TW1"),
  ("243 223 166 137", "TW2"),
  ("255 014 167 137", "TS1"),
  ("137 40 167 137", "TS2")
]


streetlights_dict = [
  ("47 34 231 89" , '1'),
  ("186 134 166 137" , '2'),
  ("78 95 166 137" , '3'),
  ("255 014 167 137" , '4'),
  ("217 117 197 89" , '4'),
  ("137 40 167 137" , '5'),
  ("01 180 166 137" , '6'),
  ("50 74 227 41" , '7'),
  ("227 134 166 137" , '8')
]

nested_leaders = [
  ("218 125 230 89", "10.9.41.216,5000")
]

emergency_dict = [
  ("27 06 231 89", "TW1"),
  ("43 180 230 89", "TW2"),
  ("78 95 166 137", "TS1"),
  ("01 180 166 137", "TS2")
]

rfid_intersections = [
  ("S3", "S4"),
  ("C1", "N4"),
  ("S5", "S4")
]


sql = "DELETE FROM traffic_lights"
c.execute(sql)
sql = "DELETE FROM nested_leaders"
c.execute(sql)
sql = "DELETE FROM emergency_rfids"
c.execute(sql)
sql = "DELETE FROM rfid_connections"
c.execute(sql)
sql = "DELETE FROM rfid_intersections"
c.execute(sql)
sql = "DELETE FROM rfid_turns"
c.execute(sql)
sql = "DELETE FROM card_id"
c.execute(sql)


try:
  sql = '''INSERT INTO traffic_lights (rfid, name) VALUES (?, ?)'''
  c.executemany(sql, traffic_light_dict)
except sqlite3.IntegrityError as e:
  print('sqlite error: ', e.args[0]) # column name is not unique
try:
  sql = '''INSERT INTO nested_leaders (rfid, connection) VALUES (?, ?)'''
  c.executemany(sql, nested_leaders)
except sqlite3.IntegrityError as e:
  print('sqlite error: ', e.args[0]) # column name is not unique
try:
  sql = '''INSERT INTO emergency_rfids (rfid, name) VALUES (?, ?)'''
  c.executemany(sql, emergency_dict)
except sqlite3.IntegrityError as e:
  print('sqlite error: ', e.args[0]) # column name is not unique
try:
  sql = '''INSERT INTO rfid_connections (current, next) VALUES (?, ?)'''
  c.executemany(sql, items)
except sqlite3.IntegrityError as e:
  print('sqlite error: ', e.args[0]) # column name is not unique
try:
  sql = '''INSERT INTO rfid_intersections (current, next) VALUES (?, ?)'''
  c.executemany(sql, rfid_intersections)
except sqlite3.IntegrityError as e:
  print('sqlite error: ', e.args[0]) # column name is not unique
try:
  sql = '''INSERT INTO rfid_turns (section, action) VALUES (?, ?)'''
  c.executemany(sql, turns)
except sqlite3.IntegrityError as e:
  print('sqlite error: ', e.args[0]) # column name is not unique
try:
  sql = '''INSERT INTO card_id (rfid, name) VALUES (?, ?)'''
  c.executemany(sql, card_id)
except sqlite3.IntegrityError as e:
  print('sqlite error: ', e.args[0]) # column name is not unique

try:
  sql = '''INSERT INTO streetlights (rfid, name) VALUES (?, ?)'''
  c.executemany(sql, streetlights_dict)
except sqlite3.IntegrityError as e:
  print('sqlite error: ', e.args[0]) # column name is not unique



conn.commit()


conn.close()

print('done')
