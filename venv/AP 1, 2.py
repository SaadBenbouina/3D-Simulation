import numpy as np
import pyvista as pv
import math
from prettytable import PrettyTable

u = 4 #Faktor für die Auflösung
#--------------AP1
table = 0

class ToolPathInterpreter:

    def nCPath(self, nc_path):
        # Initialisiere eine Tabelle mit Kopfzeilen für die Wegpunktdaten
        myTable = PrettyTable(['Number of point',"Time in min", "X", "Y", "Z",  "Vx", "Vy", "Vz", "V in mm/min", "ax", "ay", "az", "a m/s^2"])
        v, vx, vy, vz, ax, ay, az, a = 2400, 0, 0, 0, 0, 0, 0, 0
        counter, count = 0, 0
        positions, time, distance = [], [], []
        arrVx, arrVy, arrVz, arrV = [], [], [], []
        t, dist, maxacc = 0, 0.75, 10

        # Iteriere durch jede Zeile der Eingabedatei
        for index, input_line in enumerate(nc_path):
            # Verarbeite nur Zeilen, die mit "GOTO" beginnen
            if input_line.startswith("GOTO"):
                if index - 1 > 0:
                    parts = input_line.split("/")
                    coordinates = parts[1].split(",")
                    x, y, z = float(coordinates[0]), float(coordinates[1]), float(coordinates[2])
                    # Behandle den ersten Wegpunkt
                    if( len(time) == 0):
                        # Add rows
                        current_position = (x, y, z)
                        positions.append(current_position)
                        dx = abs(positions[counter][0])
                        dy = abs(positions[counter][0])
                        dz = abs(positions[counter][0])
                        d = math.sqrt(dx**2 + dy**2 + dz**2)
                        t = d/2400
                        distance.append(d)
                        arrVx.append(vx)
                        arrVy.append(vy)
                        arrVz.append(vz)
                        arrV.append(v)
                        time.append(t)
                        counter += 1
                        count +=1
                        myTable.add_row([count,round(time[counter-1],4), x, y, z,  round(vx, 2),round(vy, 2) , round(vz, 2), round(v, 2), round(ax,2), round(ay,2), round(az,2), round(a, 4)])

                    elif (len(time )>= 1):
                        # Behandle den Fall, wenn es sich um eine Kreisbewegung handelt
                        circle_line = nc_path[index -1]
                        if (circle_line.startswith("CIRCLE")  ):
                            parts_M = circle_line.split("/")
                            coordinates_M = parts_M[1].split(",")
                            x_M = float(coordinates_M[0])
                            y_M = float(coordinates_M[1])
                            z_M = float(coordinates_M[2])
                            #A is Start point
                            A = positions[counter-1]
                            M=(x_M,y_M,z_M)
                            #B ist Endepunkt
                            B=(x,y,z)
                            # Berechne den Winkel zwischen AM und MB
                            MA = (A[0]-M[0],  A[1]- M[1])
                            MB = (B[0] - M[0], B[1] - M[1])
                            norm_AM = math.sqrt(MA[0]**2 + MA[1]**2 )
                            norm_MB = math.sqrt(MB[0]**2 + MB[1]**2 )
                            dot_product = MA[0]*MB[0] + MA[1]*MB[1]
                            # Produit vectoriel de MA et MB
                            produit_vectoriel = MA[0] * MB[1] - MA[1] * MB[0]
                            winkel = math.acos(dot_product / (norm_AM * norm_MB))

                            # um jedes-mal nur 5(0.08725) grad in unsere Kreis zu gehen
                            newwinkel = 0
                            while newwinkel < winkel  :
                                if (newwinkel +0.08725> winkel) :
                                    newwinkel =winkel
                                else :
                                    newwinkel = newwinkel + 0.08725

                                if(produit_vectoriel<0) :
                                    punkt_auf_kreis = (M[0] + MA[0]*math.cos(-newwinkel)
                                                       -MA[1]*math.sin(-newwinkel),
                                                       M[1] +MA[0]*math.sin(-newwinkel)
                                                       +MA[1]*math.cos(-newwinkel),
                                                       M[2])
                                else:
                                    punkt_auf_kreis = (M[0] + MA[0]*math.cos(newwinkel)
                                                       -MA[1]*math.sin(newwinkel),
                                                       M[1] +MA[0]*math.sin(newwinkel)
                                                       +MA[1]*math.cos(newwinkel),
                                                       M[2])

                                dx = abs(punkt_auf_kreis[0] - positions[counter-1][0])
                                dy = abs(punkt_auf_kreis[1] - positions[counter-1][1])
                                dz = abs(punkt_auf_kreis[2] - positions[counter-1][2])
                                d = math.sqrt(dx**2 + dy**2 + dz**2)
                                current_position = (punkt_auf_kreis[0], punkt_auf_kreis[1], punkt_auf_kreis[2])
                                positions.append(current_position)

                                if(newwinkel<winkel):
                                    if (arrV[counter-1] == 0) :
                                        t = (d/2400) + time[counter-1]
                                    else:
                                        t = (d/arrV[counter-1]) + time[counter-1]

                                    vx = dx/(t - time[counter-1])
                                    vy = dy/(t - time[counter-1])
                                    vz = dz/(t - time[counter-1])
                                    v = (math.sqrt(vx**2 + vy**2 + vz**2))
                                    ax = (vx - arrVx[counter-1])/(3600000*(t-time[counter-1]))
                                    ay = (vy - arrVy[counter-1])/(3600000*(t-time[counter-1]))
                                    az = (vz - arrVz[counter-1])/(3600000*(t-time[counter-1]))
                                    a =math.sqrt(ax**2 + ay**2 + az**2)
                                else:
                                    vx=0
                                    vy=0
                                    vz=0
                                    v = (math.sqrt(vx**2 + vy**2 + vz**2))
                                    a = -maxacc
                                    if (arrV[counter-1] == 0) :
                                        t = (d/2400) + time[counter-1]
                                    else:
                                        t=((-arrV[counter-1]*(1/36000))/a+time[counter-1])
                                    ax = (vx - arrVx[counter-1])/(3600000*(t-time[counter-1]))
                                    ay = (vy - arrVy[counter-1])/(3600000*(t-time[counter-1]))
                                    az = (vz - arrVz[counter-1])/(3600000*(t-time[counter-1]))
                                    if(math.sqrt((ax**2 + ay**2 + az**2))):
                                        #koeffizienten rechnen
                                        k=10*math.sqrt(1/(ax**2 + ay**2 + az**2))
                                        ax *=k
                                        ay *=k
                                        az *=k
                                distance.append(d)
                                arrVx.append(vx)
                                arrVy.append(vy)
                                arrVz.append(vz)
                                arrV.append(v)
                                time.append(t)
                                counter += 1
                                count +=1
                                myTable.add_row([count,round(time[counter-1], 4), round(punkt_auf_kreis[0], 4), round(punkt_auf_kreis[1], 4), round(punkt_auf_kreis[2], 4),
                                                 round(vx, 2), round(vy, 2), round(vz, 2), round(v, 2),
                                                 round(ax, 2), round(ay, 2), round(az, 2), round(a, 4)])

                        else:

                            if(dist <= max(abs(x - positions[counter-1][0]), abs(y - positions[counter-1][1]), abs(z - positions[counter-1][2]))):
                                x1=positions[counter-1][0]
                                y1=positions[counter-1][1]
                                z1=positions[counter-1][2]
                                anzahl_punkt = math.ceil( max(abs(x - x1), abs(y - y1), abs(z - z1))*4/3)
                                count2 =1
                                while count2<= anzahl_punkt and anzahl_punkt>1   :
                                    if count2< anzahl_punkt:
                                        if abs(x1-x) >= dist and x > x1:
                                            x1 += dist
                                        elif abs(x1-x) >= dist and x < x1:
                                            x1 -= dist

                                        if abs(y - y1) >= dist and y > y1:
                                            y1 += dist
                                        elif abs(y1-y) >= dist and y < y1:
                                            y1 -= dist

                                        if abs(z - z1)>=dist and z > z1:
                                            z1 += dist
                                        elif abs(z1-z) >= dist and z < z1:
                                            z1 -= dist
                                        dx1 = abs(x1 - positions[counter-1][0])
                                        dy1 = abs(y1 - positions[counter-1][1])
                                        dz1 = abs(z1 - positions[counter-1][2])
                                        d = math.sqrt(dx1**2 + dy1**2 + dz1**2)
                                        current_position = (x1, y1, z1)
                                        positions.append(current_position)
                                        if(v==0):
                                            t = (d/2400) + time[counter-1]
                                        else:
                                            t = (d/arrV[counter-1]) + time[counter-1]

                                        vx = dx1/(t - time[counter-1])
                                        vy = dy1/(t - time[counter-1])
                                        vz = dz1/(t - time[counter-1])
                                        v = (math.sqrt(vx**2 + vy**2 + vz**2))
                                        ax = (vx - arrVx[counter-1])/(3600000*(t-time[counter-1]))
                                        ay = (vy - arrVy[counter-1])/(3600000*(t-time[counter-1]))
                                        az = (vz - arrVz[counter-1])/(3600000*(t-time[counter-1]))
                                        a =math.sqrt(ax**2 + ay**2 + az**2)
                                        distance.append(d)
                                        arrVx.append(vx)
                                        arrVy.append(vy)
                                        arrVz.append(vz)
                                        arrV.append(v)
                                        time.append(t)
                                        counter += 1
                                        count +=1
                                        count2 +=1
                                        myTable.add_row([count,round(time[counter-1],4), round(x1, 4), round(y1, 4), round(z1, 4),  round(vx, 2),round(vy, 2) , round(vz, 2), round(v, 2), round(ax,2), round(ay,2), round(az,2), round(a, 4)])
                                    else:
                                        z1=z
                                        y1=y
                                        x1=x
                                        dx1 = abs(x1 - positions[counter-1][0])
                                        dy1 = abs(y1 - positions[counter-1][1])
                                        dz1 = abs(z1 - positions[counter-1][2])
                                        d = math.sqrt(dx1**2 + dy1**2 + dz1**2)
                                        current_position = (x1, y1, z1)
                                        positions.append(current_position)
                                        vx=0
                                        vy=0
                                        vz=0
                                        v = (math.sqrt(vx**2 + vy**2 + vz**2))
                                        a = -maxacc
                                        if (arrV[counter-1] == 0) :
                                            t = (d/2400) + time[counter-1]
                                        else:
                                            t=((-arrV[counter-1]*(1/36000))/a+time[counter-1])
                                        ax = (vx - arrVx[counter-1])/(3600000*(t-time[counter-1]))
                                        ay = (vy - arrVy[counter-1])/(3600000*(t-time[counter-1]))
                                        az = (vz - arrVz[counter-1])/(3600000*(t-time[counter-1]))
                                        #koeffizienten rechnen
                                        k=10*math.sqrt(1/(ax**2 + ay**2 + az**2))
                                        ax *=k
                                        ay *=k
                                        az *=k
                                        distance.append(d)
                                        arrVx.append(vx)
                                        arrVy.append(vy)
                                        arrVz.append(vz)
                                        arrV.append(v)
                                        time.append(t)
                                        counter += 1
                                        count +=1
                                        count2 +=1
                                        myTable.add_row([count,round(time[counter-1],4), round(x1, 4), round(y1, 4), round(z1, 4),  round(vx, 2),round(vy, 2) , round(vz, 2), round(v, 2), round(ax,2), round(ay,2), round(az,2), round(a, 4)])
                            else:
                                d = math.sqrt(abs(x - positions[counter-1][0])**2 + abs(y - positions[counter-1][1])**2 + abs(z - positions[counter-1][2])**2 )
                                current_position = (x, y, z)
                                positions.append(current_position)
                                if(v==0):
                                    t = (d/2400) + time[counter-1]
                                else:
                                    t = (d/arrV[counter-1]) + time[counter-1]

                                vx = abs(x - positions[counter-1][0])/(t - time[counter-1])
                                vy = abs(y - positions[counter-1][1])/(t - time[counter-1])
                                vz = abs(z - positions[counter-1][2])/(t - time[counter-1])
                                v = (math.sqrt(vx**2 + vy**2 + vz**2))
                                ax = (vx - arrVx[counter-1])/(3600000*(t-time[counter-1]))
                                ay = (vy - arrVy[counter-1])/(3600000*(t-time[counter-1]))
                                az = (vz - arrVz[counter-1])/(3600000*(t-time[counter-1]))
                                a =math.sqrt(ax**2 + ay**2 + az**2)
                                distance.append(d)
                                arrVx.append(vx)
                                arrVy.append(vy)
                                arrVz.append(vz)
                                arrV.append(v)
                                time.append(t)
                                counter += 1
                                count += 1
                                myTable.add_row([count,round(time[counter-1],4), round(x, 4), round(y, 4), round(z, 4),  round(vx, 2),round(vy, 2) , round(vz, 2), round(v, 2), round(ax,2), round(ay,2), round(az,2), round(a, 4)])
                                vx = 0
                                vy = 0
                                vz = 0
        # Drucke die fertige Tabelle am Ende der Verarbeitung
        print(myTable)

        return  myTable


# Beispiel, um Programm auszuführen
if __name__ == "__main__":
    # Öffne die Datei im Lesemodus
    with open('ncbefehl.txt', 'r') as datei:
        # Lese jede Zeile der Datei
        nc_path = datei.readlines()

    # Erstelle eine Instanz der ToolPathInterpreter-Klasse
    tool_path_interpreter = ToolPathInterpreter()

    # Verarbeite die nc_path-Eingabe
    table = tool_path_interpreter.nCPath(nc_path)
#--------------EndeAP1

# This mesh will be the moving mesh
sphere1 = pv.Cylinder(center=(0.0, 0.0, u*50.0), direction=(0.0, 0.0, 1.0), radius=u*5, height=u*10)

pl = pv.Plotter()

#Kamera-Einstellung:
#Erklärung siehe: https://docs.pyvista.org/version/stable/api/core/camera.html
pl.camera.position = (0, 35, 300)
pl.camera.focal_point = (0, 20, 0)
pl.camera.roll = 1

pl.set_scale(xscale=1/u, yscale=1/u, zscale=1/u)

title = pl.add_text('Fachprojekt: Geometrische Modellierung von Fertigungsprozessen', position='lower_edge', color='black', shadow=True, font_size=6, font='arial')

cyl = pl.add_mesh(sphere1, color='green', line_width=5)

# for this example
pl.open_gif("movie.gif")
pl.show_grid()
pl.show(auto_close=False, interactive_update=True)

xAxis = [] # AP3
yAxis = [] # AP3
#-------------Grid

cube_1 = pv.StructuredGrid(*np.meshgrid(np.arange(-25*u, (u*25)+1), np.arange(-25*u, (u*25)+1), np.arange((u*30)+1)))
cube_1.origin = (-25*u, -25*u, 0)


#---------------------
pl.add_mesh(cube_1, show_edges=False, reset_camera=True, color='silver', diffuse=1, specular=0.2, specular_power=127.0)

count = 0
timeStempOld = 0
c = 4 # Anpassung für die Anzahl der Frames
for row in table:
    row.border = False
    row.header = False

    timeStemp = float(row.get_string(fields=["Time in min"]).strip())
    timeDelay = (timeStemp-timeStempOld) * 60
    timeStempOld = timeStemp

    x = u*float(row.get_string(fields=["X"]).strip())
    y = u*float(row.get_string(fields=["Y"]).strip())
    z = u*float(row.get_string(fields=["Z"]).strip())

    xi = int(x)+(u*25) #int-Werte
    yi = int(y)+(u*25)
    zi = int(z)


    for i in range(xi-(4), xi+(4)):
        for k in range(yi-(20), yi+(20)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi-(7), xi-(4)):
        for k in range(yi-(19), yi+(19)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi+(4), xi+(7)):
        for k in range(yi-(19), yi+(19)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi-(10), xi-(7)):
        for k in range(yi-(18), yi+(18)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi+(7), xi+(10)):
        for k in range(yi-(18), yi+(18)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi-(11), xi-(10)):
        for k in range(yi-(17), yi+(17)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi+(10), xi+(11)):
        for k in range(yi-(17), yi+(17)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi-(13), xi-(11)):
        for k in range(yi-(16), yi+(16)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi+(11), xi+(13)):
        for k in range(yi-(16), yi+(16)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi-(14), xi-(13)):
        for k in range(yi-(15), yi+(15)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi+(13), xi+(14)):
        for k in range(yi-(15), yi+(15)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi-(15), xi-(14)):
        for k in range(yi-(14), yi+(14)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi+(14), xi+(15)):
        for k in range(yi-(14), yi+(14)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi-(16), xi-(15)):
        for k in range(yi-(13), yi+(13)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi+(15), xi+(16)):
        for k in range(yi-(13), yi+(13)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi-(17), xi-(16)):
        for k in range(yi-(11), yi+(11)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi+(16), xi+(17)):
        for k in range(yi-(11), yi+(11)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi-(18), xi-(17)):
        for k in range(yi-(10), yi+(10)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi+(17), xi+(18)):
        for k in range(yi-(10), yi+(10)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi-(19), xi-(18)):
        for k in range(yi-(7), yi+(7)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi+(18), xi+(19)):
        for k in range(yi-(7), yi+(7)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi-(20), xi-(19)):
        for k in range(yi-(4), yi+(4)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center

    for i in range(xi+(19), xi+(20)):
        for k in range(yi-(4), yi+(4)):
            for j in range(zi-(5*u), zi+(10*u)):
                if i >= 0 and i < u*50 and k >= 0 and k < u*50 and j >= 0 and j < u*30:
                    centerVal =  (u*u*2500*j)+(k)+((u*50*(i))) # Koordinate in Zellenposition umgewandelt
                    cube_1.BlankCell(centerVal) #Center


    if(count == c):
        pl.remove_actor(cyl)
        sphere1 = pv.Cylinder(center=(x, y, z), direction=(0.0, 0.0, 1.0), radius=u*5, height=u*10)
        cyl = pl.add_mesh(sphere1, color='green', line_width=5)
        pl.write_frame()
        cube_1.Modified()
        count = 0

    if(count < c):
        count = count+1


print('Finish')
for _ in range(0, 10000000000000000):
    sphere1.translate([0, 0, 0], inplace=True)
    pl.write_frame()
