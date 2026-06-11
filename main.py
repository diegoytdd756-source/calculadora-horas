from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
import re

class CalculadoraAndroid(BoxLayout):
    def __init__(self, **kwargs):
        super(CalculadoraAndroid, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10

        self.dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        self.entradas = {}

        # Título
        self.add_widget(Label(text="Calculadora de Horas", font_size='24sp', bold=True, size_hint_y=None, height=40))

        # Valor Hora
        row_valor = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        row_valor.add(Label(text="Valor hora ($):", font_size='16sp', size_hint_x=0.4))
        self.txt_valor = TextInput(text="5000", input_filter='float', multiline=False, font_size='16sp')
        row_valor.add(self.txt_valor)
        self.add_widget(row_valor)

        # Contenedor con scroll para los días
        scroll = ScrollView(size_hint=(1, 0.5))
        grid_dias = GridLayout(cols=2, spacing=10, size_hint_y=None)
        grid_dias.bind(minimum_height=grid_dias.setter('height'))

        for dia in self.dias:
            grid_dias.add(Label(text=f"{dia}:", font_size='16sp', size_hint_x=0.3, halign='left'))
            # Arranca completamente limpio (vacío)
            txt = TextInput(text="", multiline=False, font_size='16sp', size_hint_y=None, height=40)
            grid_dias.add(txt)
            self.entradas[dia] = txt

        scroll.add_widget(grid_dias)
        self.add_widget(scroll)

        # Botón Calcular
        btn_calcular = Button(text="Calcular Total", font_size='18sp', bold=True, size_hint_y=None, height=50, background_color=(0, 0.5, 1, 1))
        btn_calcular.bind(on_press=self.calcular)
        self.add_widget(btn_calcular)

        # Cuadro de resultados
        self.lbl_resultado = Label(text="Resultados aquí...", font_name='Roboto', font_size='14sp', halign='left', valign='top', size_hint_y=0.3)
        self.lbl_resultado.bind(size=self.lbl_resultado.setter('text_size'))
        self.add_widget(self.lbl_resultado)

    def convertir_a_24h(self, texto_hora, es_salida=False, hora_entrada_prev=None):
        texto_hora = texto_hora.lower().replace(" ", "")
        match = re.match(r"(\d+(?:\.\d+)?)(am|pm)?", texto_hora)
        if not match: raise ValueError
        num_str, indicador = match.groups()
        hora = float(num_str)
        if indicador == "pm" and hora < 12: hora += 12
        elif indicador == "am" and hora == 12: hora = 0
        elif not indicador:
            if es_salida and hora_entrada_prev is not None and hora < hora_entrada_prev and hora < 12:
                hora += 12
            elif not es_salida and 1 <= hora <= 5:
                hora += 12
        return hora

    def calcular(self, instance):
        try:
            valor_hora = float(self.txt_valor.text)
        except ValueError:
            self.lbl_resultado.text = "Error: Valor de hora inválido."
            return

        total_horas = 0
        reporte = "REPORTE DE LA SEMANA\n" + "="*30 + "\n"

        for dia in self.dias:
            texto = self.entradas[dia].text.strip()
            if not texto or texto.lower() == "no":
                reporte += f"{dia}: 0 horas\n"
                continue

            horas_dia = 0
            for tanda in texto.split(","):
                tanda = tanda.strip()
                if "-" in tanda:
                    try:
                        inf, sup = tanda.split("-")
                        h_in = self.convertir_a_24h(inf, False)
                        h_out = self.convertir_a_24h(sup, True, h_in)
                        horas_dia += (24 - h_in) + h_out if h_out < h_in else h_out - h_in
                    except ValueError:
                        self.lbl_resultado.text = f"Error de formato en {dia} ('{tanda}')"
                        return
                else:
                    try: horas_dia += float(tanda)
                    except ValueError:
                        self.lbl_resultado.text = f"Error en {dia}"
                        return
            total_horas += horas_dia
            reporte += f"{dia}: {horas_dia} horas\n"

        reporte += "="*30 + f"\nTOTAL: {total_horas} horas\nTOTAL A COBRAR: ${total_horas * valor_hora:,.0f} COP"
        self.lbl_resultado.text = reporte

class CalculadoraApp(App):
    def build(self):
        return CalculadoraAndroid()

if __name__ == '__main__':
    CalculadoraApp().run()