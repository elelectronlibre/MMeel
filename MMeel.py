# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore, QtGui
import sqlite3
from MMeel_ui import Ui_Hucha
import re

class MMeelclass(QtGui.QMainWindow):
    def __init__(self, parent=None):
#        locale=unicode(QtCore.QLocale.system().name())
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Hucha()
        self.ui.setupUi(self)
        self.ui.dateEdit.setDate(QtCore.QDate.currentDate ())
        self.iniciarbasededatos()
        self.actualizarBase()
        self.actualizarCuentas()
        self.Centrar()
        self.editando=False
        self.DibujarTotal()
        QtCore.QObject.connect(self.ui.boton_Ok,QtCore.SIGNAL("clicked()"
        ), self.IngresarOperacion)
        QtCore.QObject.connect(self.ui.boton_Borrar,QtCore.SIGNAL("clicked()"
        ), self.BorrarOperacion)
        QtCore.QObject.connect(self.ui.boton_Editar,QtCore.SIGNAL("clicked()"
        ), self.EditarOperacion)
        QtCore.QObject.connect(self.ui.boton_Cancelar,QtCore.SIGNAL("clicked()"
        ), self.CancelarEdicion)
        QtCore.QObject.connect(self.ui.boton_Hucha,QtCore.SIGNAL("clicked()"
        ), self.DibujarHucha)
        QtCore.QObject.connect(self.ui.boton_Banco,QtCore.SIGNAL("clicked()"
        ), self.DibujarBanco)
        QtCore.QObject.connect(self.ui.boton_Total,QtCore.SIGNAL("clicked()"
        ), self.DibujarTotal)
    
    def Centrar(self):
        
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        geometria=self.ui.tableWidget.geometry()
        anchoTabla= geometria.width()
        anchoColumna = (anchoTabla-2)/5.0
        for i in range(5):
            self.ui.tableWidget.setColumnWidth(i,anchoColumna)
        
    def EditarOperacion(self):
        self.editando=True
        self.ui.boton_Cancelar.setEnabled(True)
        self.ui.boton_Borrar.setEnabled(False)
        #Esta parte es igual en la funcion BorrarOperacion
        #FIXME esta parte esta poco optimizada, se consigue la misma variable (row) de 2 maneras...
        #print 'linea seleccionada:' + linea
        self.filaeditada=self.ui.tableWidget.currentRow()
        self.elementoseditados=[]
        for i in range(5):
            itemText = self.ui.tableWidget.item(self.ui.tableWidget.currentRow(), i).text()    
            print 'itemText: ' + itemText
            self.elementoseditados.append(str(itemText))
        #insertamos los datos de la tabla en sus lugares correspondientes
        if self.elementoseditados[0]=='Ingreso': self.ui.combo_Tipo.setCurrentIndex(0)
        elif self.elementoseditados[0]=='Gasto': self.ui.combo_Tipo.setCurrentIndex(1)
        if self.elementoseditados[1]=='Banco': self.ui.combo_Lugar.setCurrentIndex(0)
        elif self.elementoseditados[1]=='Hucha': self.ui.combo_Lugar.setCurrentIndex(1)
        self.ui.text_Comentarios.setText(self.elementoseditados[2])
        self.ui.text_Cantidad.setText(self.elementoseditados[4])
        self.ui.dateEdit.setDate(QtCore.QDate.fromString(self.elementoseditados[3],"dd/MM/yyyy"))

    def CancelarEdicion(self):
        self.editando=0
        self.ui.boton_Cancelar.setEnabled(False)
        self.ui.boton_Borrar.setEnabled(True)
        
    def BorrarOperacion(self):
        #lineas=self.ui.tableWidget.selectionModel().selectedRows()
        #linea=lineas[len(lineas)-1]
        lineaSeleccionada=self.ui.tableWidget.currentRow()
        #print 'linea seleccionada:' + linea
        #fila=linea.row()
        elementos=[]
        for i in range(5):
            itemText = self.ui.tableWidget.item(lineaSeleccionada, i).text()    
            print 'itemText: ' + itemText
            elementos.append(str(itemText))
        print elementos
        
        self.cursor.execute('DELETE FROM Operaciones WHERE Tipo=? AND Lugar=? AND Comentarios=? AND Fecha=? AND Cantidad=?',(elementos[0],elementos[1],elementos[2],elementos[3],elementos[4]))
        #print fila           
        self.conexion.commit()
        self.actualizarBase()
        self.actualizarCuentas()
        
    def IngresarOperacion(self):
        
#Asignamos cada valor que queremos ingresar a una variable
        self.tipo = str(self.ui.combo_Tipo.currentText())
        self.lugar = str(self.ui.combo_Lugar.currentText())
        self.fecha = self.ui.dateEdit.date()
        self.comentario = str(self.ui.text_Comentarios.toPlainText())     
        self.cantidad = self.ui.text_Cantidad.toPlainText()
        if self.cantidad == "": self.cantidad = 0
        else: self.cantidad = float(self.cantidad)
        dia = self.fecha.day()
        mes = self.fecha.month()
        anno = self.fecha.year()
        self.fecha = str(dia) + '/' + str(mes) + '/' + str(anno)
        print self.editando
        #self.fecha=str(anno) +'-'+str(mes)+'-'+str(dia)
        if self.editando == False:
    #Pasamos los nuevos datos a la base de datos
            self.datos=(self.tipo, self.lugar, self.comentario, self.fecha,self.cantidad)
            print self.fecha
            self.cursor.execute('INSERT INTO Operaciones (Tipo,Lugar,Comentarios,Fecha,Cantidad) VALUES(?,?,?,?,?)',self.datos)
            self.conexion.commit()
            
    #Añadimos la fila nueva a la tabla
#            self.numerodefilas += 1
#            self.ui.tableWidget.setRowCount(self.numerodefilas)
#            for dato in range(len(self.datos)):
#                
#                elemento= self.datos[dato]
#                print 'elemento = ' + str(elemento)
#                item=None
#                item = QtGui.QTableWidgetItem()
#                item.setText(QtGui.QApplication.translate("Hucha", str(elemento), None, QtGui.QApplication.UnicodeUTF8))
#                self.ui.tableWidget.setItem(self.numerodefilas-1,dato,item)
            self.actualizarBase()
        elif self.editando == True:
            #Actualizamos la base de datos
            self.datoseditados=(self.tipo, self.lugar, self.comentario, self.fecha,self.cantidad,\
            self.elementoseditados[0],self.elementoseditados[1],self.elementoseditados[2],\
            self.elementoseditados[3],self.elementoseditados[4])
            print self.fecha
            #self.cursor.execute('UPDATE Operaciones SET (Tipo,Lugar,Comentarios,Fecha,Cantidad) VALUES(?,?,?,?,?) WHERE Tipo=? AND Lugar=? AND Comentarios=? AND Fecha=? AND Cantidad=?',self.datos)
            self.cursor.execute('UPDATE Operaciones SET Tipo=?,Lugar=?,Comentarios=?,Fecha=?,Cantidad=? WHERE Tipo=? AND Lugar=? AND Comentarios=? AND Fecha=? AND Cantidad=?',self.datoseditados)
            self.conexion.commit()
            
            #Editamos la fila ...
#            self.datos=(self.tipo, self.lugar, self.comentario, self.fecha,self.cantidad)
#            for dato in range(5):
#                
#                elemento= self.datos[dato]
#                print 'elemento = ' + str(elemento)
#                item=None
#                item = QtGui.QTableWidgetItem()
#                item.setText(QtGui.QApplication.translate("Hucha", str(elemento), None, QtGui.QApplication.UnicodeUTF8))
#                self.ui.tableWidget.setItem(self.numerodefilas-1,dato,item)
            self.editando=0
            self.ui.boton_Cancelar.setEnabled(False)
            self.ui.boton_Borrar.setEnabled(True)
            self.actualizarBase( )
        self.actualizarCuentas()
        
        print str(anno) +'-'+str(mes)+'-'+str(dia)
        
        print self.comentario
        print self.cantidad
        #print self.fecha
        #self.fecha = self.fecha.toString(QtCore.QDate.ISODate())
        print self.lugar
        print self.tipo
        
        #item = QtGui.QTableWidgetItem()
        #item.setText(QtGui.QApplication.translate("Hucha", "Operacionrealizada", None, QtGui.QApplication.UnicodeUTF8))
        #self.ui.tableWidget.setItem(0, 0, item)

    def iniciarbasededatos(self):
        import os.path
        camino = os.path.abspath('basehucha.db')
        print camino
        print os.path.isfile(camino)
#Si la base de datos existe, la cargamos; si no, la creamos
        if not os.path.isfile(camino):
            self.conexion = sqlite3.connect('basehucha.db')
            print 'Base creada'
            self.cursor = self.conexion.cursor()
            self.cursor.execute("CREATE TABLE Operaciones (Id INTEGER PRIMARY KEY, Tipo TEXT, Lugar TEXT, Comentarios TEXT, Fecha TEXT, Cantidad INT)")
            print 'Tabla creada'
            self.conexion.commit()
        else:
            self.conexion = sqlite3.connect('basehucha.db')
            print 'Base conectada'
            self.cursor = self.conexion.cursor()

    def actualizarBase(self):
        
#Cargamos la base de datos y la colocamos en la tabla

        self.cursor.execute("SELECT * FROM Operaciones")
        filas = self.cursor.fetchall()
        self.numerodefilas=len(filas)
        self.ui.tableWidget.setRowCount(self.numerodefilas)
        #print filas[0]
        self.listatotal = []
        for j in range(self.numerodefilas):

            fila = filas[j]
            for i in range(1,len(fila)):
                elemento = fila[i]
                print 'elemento= '+ str(elemento)
                #print i
                elemento = str(elemento)
                #Da complicaciones al manejar los datos if i == 5 : elemento = elemento + '€'
                if elemento == 'None' : elemento = ' '
                item=None
                item = QtGui.QTableWidgetItem()
                item.setText(QtGui.QApplication.translate("Hucha", str(elemento), None, QtGui.QApplication.UnicodeUTF8))
                self.ui.tableWidget.setItem(j,i-1,item)  
            self.listatotal.append((fila[1], fila[2], fila[4], fila[5])) #self.listatotal es una lista de tuplas, cada tupla es 
            print self.listatotal
            
            
        

    
    def actualizarCuentas(self):
        self.hucha=0
        self.banco=0
        self.total=0
        self.cursor.execute("SELECT * FROM Operaciones")
        filas = self.cursor.fetchall()
        for j in range(self.numerodefilas):
            fila = filas[j]
            if fila[2].lower() == 'hucha':
                if fila[1].lower() == 'ingreso':
                    self.hucha += float(fila[5])
                elif fila[1].lower() == 'gasto':
                    self.hucha -= float(fila[5])
            elif fila[2].lower() == 'banco':
                if fila[1].lower() == 'ingreso':
                    self.banco += float(fila[5])
                elif fila[1].lower() == 'gasto':
                    self.banco -= float(fila[5])
        self.total=self.banco + self.hucha
        self.ui.label_Hucha.setText(str(self.hucha))
        self.ui.label_Banco.setText(str(self.banco))
        self.ui.label_Total.setText(str(self.total))
        
#    def ParseTable(self,filtro):
#        for fila in range(self.numerodefilas):
#            for columna in range(4):
                
    
#    def DibujarTotal(self, tipo):
#        lista=[]
#        suma=0
#        for operacion in range(self.numerodefilas):
#            fila = self.listatotal[operacion]
#            
    def DibujarTotal(self):
 
        if self.numerodefilas is not 0:
            lista=[]
            operaciones = []
            x = []
            suma=0
            self.ui.mpl.canvas.ax1.clear()        
            self.ui.mpl.canvas.ax2.clear()
            self.ui.mpl.canvas.width= 600
            self.ui.mpl.canvas.ax1.axes.set_xlim(0,self.numerodefilas)
            self.ui.mpl.canvas.ax1.axes.set_ylabel('Operaciones')
            self.ui.mpl.canvas.ax2.axes.set_ylabel('Total', color='blue')
            self.ui.mpl.canvas.ax1.axhline(y=0, color='black')
            self.ui.mpl.canvas.ax2.axhline(y=0, color='black')
            ancho = 0.5
            for operacion in range(self.numerodefilas):
                fila = self.listatotal[operacion]
                print 'datos= ' + str(len(fila)) + '  ' + str(fila[3])
                operaciones.append(fila[3])
                if fila[0] == 'Ingreso':
                    suma += fila[3]
                    self.ui.mpl.canvas.ax1.bar(operacion+ancho/2-operacion/self.numerodefilas,fila[3], width=ancho,  color = 'green')
                elif fila[0] == 'Gasto':
                    suma -= fila[3]
                    self.ui.mpl.canvas.ax1.bar(operacion+ancho/2-operacion/self.numerodefilas,-fila[3], width=ancho,  color='red')
                lista.append(suma)
                x.append(operacion+ancho-operacion/self.numerodefilas)
            print operaciones
            self.ui.mpl.canvas.ax1.set_ylim(-1.1*max(operaciones),1.1*max(operaciones))            
                #print 'LISTA= ' +  str(lista)
            self.ui.mpl.canvas.ax2.plot(x,lista, '-o', color='blue')
            self.ui.mpl.canvas.draw()

    def DibujarHucha(self):
        self.ui.mpl.canvas.ax1.clear()        
        self.ui.mpl.canvas.ax2.clear()
        if self.numerodefilas is not 0:
            lista=[]
            operaciones = []
            x=[]
            suma=0
    #        if re.match(self.listatotal,'Hucha'): numerofilas = match.group(1)
            self.ui.mpl.canvas.ax1.clear()        
            self.ui.mpl.canvas.ax2.clear()
            self.ui.mpl.canvas.width= 600
    
            self.ui.mpl.canvas.ax1.axes.set_ylabel('Operaciones')
            self.ui.mpl.canvas.ax2.axes.set_ylabel('Total', color='blue')
            self.ui.mpl.canvas.ax1.axhline(y=0, color='black')
            self.ui.mpl.canvas.ax2.axhline(y=0, color='black')
            ancho = 0.5
            huchatotal = 0
            for operacion in range(self.numerodefilas):
                fila = self.listatotal[operacion]            
                if fila[1] == 'Hucha': 
                    huchatotal += 1
                    operaciones.append(fila[3])
            if huchatotal is not 0:
                for operacion in range(self.numerodefilas):
                    fila = self.listatotal[operacion]
                    if fila[1] == 'Hucha':
                        x.append(len(lista)-(len(lista))/huchatotal+ ancho)
                        if fila[0] == 'Ingreso':
                            self.ui.mpl.canvas.ax1.bar(len(lista)-(len(lista))/huchatotal+ ancho/2,fila[3], width=ancho,  color = 'green')
                            suma += fila[3]
                            lista.append(suma)
                            print 'altura' + str(fila[3])
                        elif fila[0] == 'Gasto':
                            
                            self.ui.mpl.canvas.ax1.bar(len(lista)-(len(lista))/huchatotal + ancho/2,-fila[3], width=ancho,  color='red')
                            suma -= fila[3]
                            lista.append(suma)
                        
                    
                    print 'LISTA= ' +  str(lista)
                self.ui.mpl.canvas.ax1.axes.set_xlim(0,huchatotal)
                self.ui.mpl.canvas.ax1.set_ylim(-1.1*max(operaciones),1.1*max(operaciones)) 
                print 'max' + str(max(lista))
                self.ui.mpl.canvas.ax2.plot(x,lista,'-o', color='blue')
        self.ui.mpl.canvas.draw()
        
    def DibujarBanco(self):
        self.ui.mpl.canvas.ax1.clear()        
        self.ui.mpl.canvas.ax2.clear()
        if self.numerodefilas is not 0:
            lista=[]
            operaciones = []
            x = []
            suma=0
            ancho = 0.2
            self.ui.mpl.canvas.ax1.clear()        
            self.ui.mpl.canvas.ax2.clear()
            self.ui.mpl.canvas.width= 600
            self.ui.mpl.canvas.ax1.axes.set_xlim(0,self.numerodefilas)
            self.ui.mpl.canvas.ax1.axes.set_ylabel('Operaciones')
            self.ui.mpl.canvas.ax2.axes.set_ylabel('Total', color='blue')
            self.ui.mpl.canvas.ax1.axhline(y=0, color='black')
            self.ui.mpl.canvas.ax2.axhline(y=0, color='black')
            ancho = 0.5
            bancototal=0
            
            for operacion in range(self.numerodefilas):
                fila = self.listatotal[operacion]            
                if fila[1] == 'Banco': 
                    bancototal += 1
                    operaciones.append(fila[3])
                print 'bancototal' + str(bancototal)
                
            if bancototal is not 0:
                for operacion in range(self.numerodefilas):
                    fila = self.listatotal[operacion]
                    if fila[1] == 'Banco':
                        x.append(len(lista)-(len(lista))/bancototal + ancho)
                        if fila[0] == 'Ingreso':
                            self.ui.mpl.canvas.ax1.bar(len(lista)-(len(lista))/bancototal + ancho/2 ,fila[3], width=ancho,  color = 'green')
                            suma += fila[3]
                            lista.append(suma)
                        elif fila[0] == 'Gasto':
        
                            self.ui.mpl.canvas.ax1.bar(len(lista)-(len(lista))/bancototal + ancho/2,-fila[3], width=ancho,  color='red')
                            suma -= fila[3]
                            lista.append(suma)
                        
        
                self.ui.mpl.canvas.ax1.set_ylim(-1.1*max(operaciones),1.1*max(operaciones))         
                self.ui.mpl.canvas.ax1.axes.set_xlim(0,bancototal )
                self.ui.mpl.canvas.ax2.plot(x,lista,'-o', color='blue')
        self.ui.mpl.canvas.draw()
        
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    gestor = MMeelclass()
    gestor.show()
    sys.exit(app.exec_())
