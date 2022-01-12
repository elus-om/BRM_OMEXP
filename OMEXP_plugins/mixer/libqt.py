from qtpy import QtCore, QtGui, QtWidgets

class LimistDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent, max_db):
        super(LimistDelegate, self).__init__(parent)
        self.max_db = max_db

    def createEditor(self, parent, option, index):
        editor = super(LimistDelegate, self).createEditor(parent, option, index)
        # Specify which column will use the spin box because number can be line edit
        if index.column() == 1: # Channel
            editor = QtWidgets.QLineEdit(parent)
            regexp = QtCore.QRegularExpression("^((,|,\s|\d+)+)$")
            valid = QtGui.QRegularExpressionValidator(regexp)
            editor.setValidator(valid)
        elif index.column() == 2: # Level
            regexp = QtCore.QRegularExpression("[0-9]+|([0-9]+\.+[0-9]+)|(\[([A-Z]|[a-z]|\_)+\])")
            valid = QtGui.QRegularExpressionValidator(regexp)
            editor.setValidator(valid)
            #editor.setRange(0, self.max_db)
        elif index.column() in (3, 4):
            editor = QtWidgets.QDoubleSpinBox(parent)
            editor.setRange(0, 10)
        elif index.column() in (5, 6): 
            editor = QtWidgets.QLineEdit(parent)
            regexp = QtCore.QRegularExpression("(([a-z]|[A-Z])\w+|\s*|[0-9]+)+")
            valid = QtGui.QRegularExpressionValidator(regexp)
            editor.setValidator(valid)
        return editor
 
    def setModelData(self, editor, model, index):
        if index.column() == 2: # Level
            editor = check_value(editor, self.max_db)
        #print(editor.validator().validate(editor.text(), 0))
        super(LimistDelegate, self).setModelData(editor, model, index)

    def setEditorData(self, editor, index):
        # When setting the data in the editor
        if index.column() == 2: # Level
            editor = check_value(editor, self.max_db)
        super(LimistDelegate, self).setEditorData(editor, index)

def check_value(editor, maximum):
    try:
        val = float(editor.text())
        val = min(val, maximum)
        editor.setText(str(val))
    except ValueError:
        pass
    return editor
    
#def create_table():
#    nrows, ncols = random.randrange(3, 6), 3
#    table = QtWidgets.QTableWidget(nrows, ncols)
#    for r in range(nrows):
#        text = "description {}".format(r)
#        a = random.randrange(0, 180) 
#        b = random.randrange(a, 360)
#        for c, val in enumerate([text, a, b]):
#            it = QtWidgets.QTableWidgetItem()
#            it.setData(QtCore.Qt.DisplayRole, val) # set data on item
#            table.setItem(r, c, it)
#    return table
 
#class Widget(QtWidgets.QWidget):
#    def __init__(self, parent=None):
#        super(Widget, self).__init__(parent)
#        vlay = QtWidgets.QVBoxLayout(self)
       
#        table = create_table()
#        delegate = LimistDelegate(table) # create delegate
#        table.setItemDelegate(delegate)  # set delegate
#        vlay.addWidget(table)
 
#if __name__ == '__main__':
#    import sys
#    app = QtWidgets.QApplication(sys.argv)
#    w = Widget()
#    w.show()
#    sys.exit(app.exec_())
    #validator = "^((,|,\s|\d+)+)$"