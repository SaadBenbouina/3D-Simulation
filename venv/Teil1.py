import math



from prettytable import PrettyTable


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




# Beispiel, um Programm auszuführen
if __name__ == "__main__":
    # Öffne die Datei im Lesemodus
    with open('ncbefehl.txt', 'r') as datei:
        # Lese jede Zeile der Datei
        nc_path = datei.readlines()

    # Erstelle eine Instanz der ToolPathInterpreter-Klasse
    tool_path_interpreter = ToolPathInterpreter()

    # Verarbeite die nc_path-Eingabe
    tool_path_interpreter.nCPath(nc_path)
