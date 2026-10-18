import sqlite3
import random

conn = sqlite3.connect("sql_app.db")
c = conn.cursor()

# 1. Update transfers for existing players who moved to modern clubs
TRANSFERS = [
    # Fulham
    ("Bernd Leno", "Fulham", "Premier League"),
    ("Emile Smith Rowe", "Fulham", "Premier League"),
    ("Alex Iwobi", "Fulham", "Premier League"),
    ("Timothy Castagne", "Fulham", "Premier League"),
    ("Joachim Andersen", "Fulham", "Premier League"),
    ("Adama Traoré", "Fulham", "Premier League"),
    ("Raúl Jiménez", "Fulham", "Premier League"),
    ("Harrison Reed", "Fulham", "Premier League"),
    ("Kenny Tete", "Fulham", "Premier League"),
    ("Harry Wilson", "Fulham", "Premier League"),
    ("Andreas Pereira", "Fulham", "Premier League"),

    # Bournemouth
    ("Kepa Arrizabalaga", "Bournemouth", "Premier League"),
    ("Tyler Adams", "Bournemouth", "Premier League"),
    ("Philip Billing", "Bournemouth", "Premier League"),
    ("Ryan Christie", "Bournemouth", "Premier League"),
    ("Lewis Cook", "Bournemouth", "Premier League"),
    ("Adam Smith", "Bournemouth", "Premier League"),
    ("Mark Travers", "Bournemouth", "Premier League"),
    ("Marcos Senesi", "Bournemouth", "Premier League"),
    ("Marcus Tavernier", "Bournemouth", "Premier League"),
    ("Justin Kluivert", "Bournemouth", "Premier League"),
    ("Enes Ünal", "Bournemouth", "Premier League"),
    ("Dango Ouattara", "Bournemouth", "Premier League"),

    # Nottingham Forest
    ("Matz Sels", "Nottingham Forest", "Premier League"),
    ("Ola Aina", "Nottingham Forest", "Premier League"),
    ("Taiwo Awoniyi", "Nottingham Forest", "Premier League"),
    ("Callum Hudson-Odoi", "Nottingham Forest", "Premier League"),
    ("Anthony Elanga", "Nottingham Forest", "Premier League"),
    ("Morgan Gibbs-White", "Nottingham Forest", "Premier League"),
    ("Chris Wood", "Nottingham Forest", "Premier League"),
    ("Willy Boly", "Nottingham Forest", "Premier League"),
    ("Neco Williams", "Nottingham Forest", "Premier League"),
    ("Ryan Yates", "Nottingham Forest", "Premier League"),
    ("Nicolás Domínguez", "Nottingham Forest", "Premier League"),
    ("Ibrahim Sangaré", "Nottingham Forest", "Premier League"),
    ("Álex Moreno", "Nottingham Forest", "Premier League"),
    ("Nikola Milenković", "Nottingham Forest", "Premier League"),

    # Girona
    ("Donny van de Beek", "Girona", "La Liga"),
    ("Miguel Gutiérrez", "Girona", "La Liga"),
    ("Yangel Herrera", "Girona", "La Liga"),
    ("Iván Martín", "Girona", "La Liga"),
    ("Daley Blind", "Girona", "La Liga"),
    ("David López", "Girona", "La Liga"),
    ("Oriol Romeu", "Girona", "La Liga"),
    ("Portu", "Girona", "La Liga"),
    ("Juanpe", "Girona", "La Liga"),
    ("Bryan Gil", "Girona", "La Liga"),
    ("Arnau Martínez", "Girona", "La Liga"),
    ("Cristhian Stuani", "Girona", "La Liga"),
    ("Viktor Tsygankov", "Girona", "La Liga"),
    ("Abel Ruiz", "Girona", "La Liga"),
    ("Paulo Gazzaniga", "Girona", "La Liga"),

    # Como
    ("Pepe Reina", "Como", "Serie A"),
    ("Emil Audero", "Como", "Serie A"),
    ("Sergi Roberto", "Como", "Serie A"),
    ("Andrea Belotti", "Como", "Serie A"),
    ("Patrick Cutrone", "Como", "Serie A"),
    ("Alberto Moreno", "Como", "Serie A"),
    ("Daniele Baselli", "Como", "Serie A"),
    ("Simone Verdi", "Como", "Serie A"),
    ("Gabriel Strefezza", "Como", "Serie A"),
    ("Edoardo Goldaniga", "Como", "Serie A"),
    ("Alberto Dossena", "Como", "Serie A"),
    ("Nico Paz", "Como", "Serie A"),

    # Parma
    ("Matteo Cancellieri", "Parma", "Serie A"),
    ("Pontus Almqvist", "Parma", "Serie A"),
    ("Hernani", "Parma", "Serie A"),
    ("Yordan Osorio", "Parma", "Serie A"),
    ("Leandro Chichizola", "Parma", "Serie A"),
    ("Dennis Man", "Parma", "Serie A"),
    ("Valentin Mihăilă", "Parma", "Serie A"),
    ("Adrián Bernabé", "Parma", "Serie A"),
    ("Simon Sohm", "Parma", "Serie A"),
    ("Enrico Delprato", "Parma", "Serie A"),

    # Lecce
    ("Wladimiro Falcone", "Lecce", "Serie A"),
    ("Ante Rebić", "Lecce", "Serie A"),
    ("Rémi Oudin", "Lecce", "Serie A"),
    ("Kevin Bonifazi", "Lecce", "Serie A"),
    ("Frédéric Guilbert", "Lecce", "Serie A"),
    ("Federico Baschirotto", "Lecce", "Serie A"),
    ("Antonino Gallo", "Lecce", "Serie A"),
    ("Ylber Ramadani", "Lecce", "Serie A"),
    ("Nikola Krstović", "Lecce", "Serie A"),
    ("Lameck Banda", "Lecce", "Serie A"),

    # Werder Bremen
    ("Niklas Stark", "Werder Bremen", "Bundesliga"),
    ("Leonardo Bittencourt", "Werder Bremen", "Bundesliga"),
    ("Anthony Jung", "Werder Bremen", "Bundesliga"),
    ("Miloš Veljković", "Werder Bremen", "Bundesliga"),
    ("Marco Friedl", "Werder Bremen", "Bundesliga"),
    ("Mitchell Weiser", "Werder Bremen", "Bundesliga"),
    ("Marvin Ducksch", "Werder Bremen", "Bundesliga"),
    ("Jens Stage", "Werder Bremen", "Bundesliga"),
    ("Romano Schmid", "Werder Bremen", "Bundesliga"),
    ("Michael Zetterer", "Werder Bremen", "Bundesliga"),
    ("Senne Lynen", "Werder Bremen", "Bundesliga"),

    # FC Barcelona
    ("Dani Olmo", "FC Barcelona", "La Liga"),
    ("Robert Lewandowski", "FC Barcelona", "La Liga"),
    ("Jules Koundé", "FC Barcelona", "La Liga"),
    ("Andreas Christensen", "FC Barcelona", "La Liga"),
    ("Iñigo Martínez", "FC Barcelona", "La Liga"),
    ("Fermín López", "FC Barcelona", "La Liga"),

    # Real Madrid
    ("Kylian Mbappé", "Real Madrid", "La Liga"),
    ("Jude Bellingham", "Real Madrid", "La Liga"),
    ("Arda Güler", "Real Madrid", "La Liga"),
    ("Fran García", "Real Madrid", "La Liga"),
    ("Joselu", "Real Madrid", "La Liga"),

    # Atletico Madrid
    ("Robin Le Normand", "Atlético Madrid", "La Liga"),
    ("Conor Gallagher", "Atlético Madrid", "La Liga"),
    ("Alexander Sørloth", "Atlético Madrid", "La Liga"),
    ("Julián Álvarez", "Atlético Madrid", "La Liga"),

    # Juventus
    ("Douglas Luiz", "Juventus", "Serie A"),
    ("Teun Koopmeiners", "Juventus", "Serie A"),
    ("Khéphren Thuram", "Juventus", "Serie A"),
    ("Nicolás González", "Juventus", "Serie A"),
    ("Pierre Kalulu", "Juventus", "Serie A"),

    # Arsenal
    ("Riccardo Calafiori", "Arsenal", "Premier League"),
    ("Mikel Merino", "Arsenal", "Premier League"),
    ("Raheem Sterling", "Arsenal", "Premier League"),
    ("Kai Havertz", "Arsenal", "Premier League"),
    ("Declan Rice", "Arsenal", "Premier League"),
    ("Jurriën Timber", "Arsenal", "Premier League"),
    ("David Raya", "Arsenal", "Premier League"),

    # Chelsea
    ("Cole Palmer", "Chelsea", "Premier League"),
    ("Nicolas Jackson", "Chelsea", "Premier League"),
    ("Moisés Caicedo", "Chelsea", "Premier League"),
    ("Enzo Fernández", "Chelsea", "Premier League"),
    ("Pedro Neto", "Chelsea", "Premier League"),
    ("Jadon Sancho", "Chelsea", "Premier League"),
    ("Christopher Nkunku", "Chelsea", "Premier League"),
    ("Malo Gusto", "Chelsea", "Premier League"),
    ("Noni Madueke", "Chelsea", "Premier League"),
    ("Levi Colwill", "Chelsea", "Premier League"),

    # Bayern Munich
    ("Michael Olise", "Bayern Munich", "Bundesliga"),
    ("João Palhinha", "Bayern Munich", "Bundesliga"),
    ("Harry Kane", "Bayern Munich", "Bundesliga"),
    ("Kim Min-jae", "Bayern Munich", "Bundesliga"),
    ("Raphaël Guerreiro", "Bayern Munich", "Bundesliga"),
    ("Konrad Laimer", "Bayern Munich", "Bundesliga"),

    # Borussia Dortmund
    ("Serhou Guirassy", "Borussia Dortmund", "Bundesliga"),
    ("Waldemar Anton", "Borussia Dortmund", "Bundesliga"),
    ("Pascal Groß", "Borussia Dortmund", "Bundesliga"),
    ("Maximilian Beier", "Borussia Dortmund", "Bundesliga"),
    ("Marcel Sabitzer", "Borussia Dortmund", "Bundesliga"),
    ("Felix Nmecha", "Borussia Dortmund", "Bundesliga"),

    # Bayer Leverkusen
    ("Granit Xhaka", "Bayer Leverkusen", "Bundesliga"),
    ("Álex Grimaldo", "Bayer Leverkusen", "Bundesliga"),
    ("Victor Boniface", "Bayer Leverkusen", "Bundesliga"),
    ("Jonas Hofmann", "Bayer Leverkusen", "Bundesliga"),
    ("Aleix García", "Bayer Leverkusen", "Bundesliga"),
    ("Martin Terrier", "Bayer Leverkusen", "Bundesliga"),

    # Napoli
    ("Romelu Lukaku", "Napoli", "Serie A"),
    ("Scott McTominay", "Napoli", "Serie A"),
    ("Billy Gilmour", "Napoli", "Serie A"),
    ("David Neres", "Napoli", "Serie A"),
    ("Alessandro Buongiorno", "Napoli", "Serie A"),

    # Marseille
    ("Mason Greenwood", "Olympique de Marseille", "Ligue 1"),
    ("Pierre-Emile Højbjerg", "Olympique de Marseille", "Ligue 1"),
    ("Adrien Rabiot", "Olympique de Marseille", "Ligue 1"),
    ("Gerónimo Rulli", "Olympique de Marseille", "Ligue 1"),
    ("Elye Wahi", "Olympique de Marseille", "Ligue 1"),

    # PSG
    ("João Neves", "Paris Saint-Germain", "Ligue 1"),
    ("Willian Pacho", "Paris Saint-Germain", "Ligue 1"),
    ("Désiré Doué", "Paris Saint-Germain", "Ligue 1"),
    ("Ousmane Dembélé", "Paris Saint-Germain", "Ligue 1"),
    ("Lucas Beraldo", "Paris Saint-Germain", "Ligue 1"),
    ("Bradley Barcola", "Paris Saint-Germain", "Ligue 1")
]

updated_transfers = 0
for name, team, league in TRANSFERS:
    c.execute("UPDATE players SET team = ?, league = ? WHERE name = ?", (team, league, name))
    if c.rowcount > 0:
        updated_transfers += c.rowcount

conn.commit()
print(f"Updated club affiliations for {updated_transfers} star player records.")

conn.close()
