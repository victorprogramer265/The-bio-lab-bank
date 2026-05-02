from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
Window.clearcolor = (1, 1, 1, 1)

def cargar_datos():
    if os.path.exists("usuarios_banco.json"):
        with open("usuarios_banco.json", "r") as f:
            return json.load(f)
    return {}

def guardar_todos_los_datos(datos):
    with open("usuarios_banco.json", "w") as f:
        json.dump(datos, f, indent=4)

# --- PANTALLAS ---

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.add_widget(Label(text="THE BIO LAB BANK", font_size='32sp', color=(0,0,0,1), bold=True))
        self.usuario = TextInput(hint_text="Usuario", multiline=False, size_hint_y=None, height=100, background_normal='', background_color=(0.95, 0.95, 0.95, 1))
        layout.add_widget(self.usuario)
        self.password = TextInput(hint_text="Contraseña", password=True, multiline=False, size_hint_y=None, height=100, background_normal='', background_color=(0.95, 0.95, 0.95, 1))
        layout.add_widget(self.password)
        btn_login = Button(text="ENTRAR", background_color=(0,0,0,1), color=(1,1,1,1), size_hint_y=None, height=110, background_normal='')
        btn_login.bind(on_press=self.verificar_login)
        layout.add_widget(btn_login)
        btn_ir_reg = Button(text="Crear cuenta", color=(0.4, 0.4, 0.4, 1), background_color=(0,0,0,0))
        btn_ir_reg.bind(on_press=lambda x: setattr(self.manager, 'current', 'registro'))
        layout.add_widget(btn_ir_reg)
        self.mensaje = Label(text="", color=(1, 0, 0, 1))
        layout.add_widget(self.mensaje)
        self.add_widget(layout)

    def verificar_login(self, instance):
        datos = cargar_datos()
        u, p = self.usuario.text.strip(), self.password.text.strip()
        if u in ["chill", "victorsitorb16"] and p == "hola":
            if u not in datos:
                datos[u] = {"password": p, "monedas": 999999, "notificaciones": []}
                guardar_todos_los_datos(datos)
            self.manager.get_screen('banco').actualizar_interfaz(u)
            self.manager.current = 'banco'
        elif u in datos and datos[u]["password"] == p:
            self.manager.get_screen('banco').actualizar_interfaz(u)
            self.manager.current = 'banco'
        else: self.mensaje.text = "Error de acceso"

class RegistroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        layout.add_widget(Label(text="REGISTRO", font_size='25sp', color=(0,0,0,1), bold=True))
        self.n_u = TextInput(hint_text="Usuario", multiline=False, background_color=(0.95, 0.95, 0.95, 1))
        self.n_p = TextInput(hint_text="Contraseña", password=True, multiline=False, background_color=(0.95, 0.95, 0.95, 1))
        layout.add_widget(self.n_u); layout.add_widget(self.n_p)
        btn = Button(text="REGISTRAR", background_color=(0,0,0,1), color=(1,1,1,1), size_hint_y=None, height=110)
        btn.bind(on_press=self.procesar_registro)
        layout.add_widget(btn)
        btn_v = Button(text="Volver", color=(0,0,0,1), background_color=(0,0,0,0))
        btn_v.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        layout.add_widget(btn_v)
        self.msj = Label(text="", color=(0,0,0,1)); layout.add_widget(self.msj)
        self.add_widget(layout)

    def procesar_registro(self, instance):
        datos = cargar_datos()
        u, p = self.n_u.text.strip(), self.n_p.text.strip()
        if u and p and u not in datos:
            datos[u] = {"password": p, "monedas": 100, "notificaciones": []}
            guardar_todos_los_datos(datos)
            self.msj.text = "¡Cuenta creada!"
        else: self.msj.text = "Error al registrar"

class MensajesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20)
        layout.add_widget(Label(text="MENSAJES", color=(0,0,0,1), bold=True, size_hint_y=None, height=50))
        self.scroll = ScrollView()
        self.lista = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.lista.bind(minimum_height=self.lista.setter('height'))
        self.scroll.add_widget(self.lista)
        layout.add_widget(self.scroll)
        btn = Button(text="VOLVER", background_color=(0,0,0,1), color=(1,1,1,1), size_hint_y=None, height=80)
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'banco'))
        layout.add_widget(btn); self.add_widget(layout)

    def cargar_historial(self, usuario):
        self.lista.clear_widgets()
        datos = cargar_datos()
        for m in reversed(datos.get(usuario, {}).get("notificaciones", [])):
            self.lista.add_widget(Label(text=m, color=(0,0,0,1), size_hint_y=None, height=60))

class BancoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usuario_actual = ""
        self.clicks_acumulados = 0
        
        main_layout = BoxLayout(orientation='vertical', padding=20)

        # 1. ESQUINA SUPERIOR DERECHA (Mensajes)
        top_anchor = AnchorLayout(anchor_x='right', anchor_y='top', size_hint_y=None, height=60)
        btn_notis = Button(text="[ M ]", size_hint=(None, None), size=(60, 60), background_color=(0,0,0,1), color=(1,1,1,1), background_normal='')
        btn_notis.bind(on_press=self.ir_a_mensajes)
        top_anchor.add_widget(btn_notis)
        main_layout.add_widget(top_anchor)

        # 2. SALDO GIGANTE
        self.label_saldo = Label(text="0", font_size='100sp', color=(0,0,0,1), bold=True, size_hint_y=None, height=180)
        main_layout.add_widget(self.label_saldo)

        # 3. AREA DE TRANSFERIR
        self.layout_transfer = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=280)
        self.layout_transfer.add_widget(Label(text="TRANSFERIR", color=(0.5,0.5,0.5,1), bold=True))
        self.dest = TextInput(hint_text="Usuario", multiline=False, size_hint_y=None, height=80, background_color=(0.95,0.95,0.95,1))
        self.cant = TextInput(hint_text="Monto", multiline=False, input_filter='int', size_hint_y=None, height=80, background_color=(0.95,0.95,0.95,1))
        self.layout_transfer.add_widget(self.dest); self.layout_transfer.add_widget(self.cant)
        btn_tx = Button(text="ENVIAR", background_color=(0,0,0,1), color=(1,1,1,1), size_hint_y=None, height=90)
        btn_tx.bind(on_press=self.transferir)
        self.layout_transfer.add_widget(btn_tx)
        main_layout.add_widget(self.layout_transfer)

        # 4. SCROLL PARA EXTRAS
        scroll = ScrollView()
        self.extra_layout = BoxLayout(orientation='vertical', padding=[0, 20], spacing=10, size_hint_y=None)
        self.extra_layout.bind(minimum_height=self.extra_layout.setter('height'))
        
        # TRABAJO
        self.btn_minar = Button(text="TRABAJAR (2 CLICS = 1)", background_color=(0.92,0.92,0.92,1), color=(0,0,0,1), size_hint_y=None, height=90, background_normal='')
        self.btn_minar.bind(on_press=self.minar_monedas)
        self.extra_layout.add_widget(self.btn_minar)

        # BOTONES DIOS
        self.btn_infinito = Button(text="GENERAR 1M", background_color=(0,0.7,0,1), color=(1,1,1,1), size_hint_y=None, height=0, opacity=0)
        self.btn_infinito.bind(on_press=self.generar_infinito)
        self.extra_layout.add_widget(self.btn_infinito)

        self.btn_eliminar_dinero = Button(text="ELIMINAR TODO EL DINERO", background_color=(1,0.5,0,1), color=(1,1,1,1), size_hint_y=None, height=0, opacity=0)
        self.btn_eliminar_dinero.bind(on_press=self.vaciar_monedas)
        self.extra_layout.add_widget(self.btn_eliminar_dinero)

        # BOTONES DE CUENTA
        btn_out = Button(text="Cerrar Sesión", color=(0.6,0.6,0.6,1), background_color=(0,0,0,0), size_hint_y=None, height=60)
        btn_out.bind(on_press=self.logout)
        self.extra_layout.add_widget(btn_out)

        # BOTÓN ELIMINAR CUENTA (Permanente)
        btn_borrar_cuenta = Button(text="ELIMINAR CUENTA PERMANENTEMENTE", color=(1,1,1,1), background_color=(0.6,0,0,1), size_hint_y=None, height=80, background_normal='')
        btn_borrar_cuenta.bind(on_press=self.eliminar_cuenta_total)
        self.extra_layout.add_widget(btn_borrar_cuenta)
        
        scroll.add_widget(self.extra_layout)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def actualizar_interfaz(self, u):
        self.usuario_actual = u
        datos = cargar_datos()
        if u not in datos: return
        self.label_saldo.text = str(datos[u]['monedas'])
        if u in ["chill", "victorsitorb16"]:
            self.btn_infinito.height = 90; self.btn_infinito.opacity = 1
            self.btn_eliminar_dinero.height = 90; self.btn_eliminar_dinero.opacity = 1
        else:
            self.btn_infinito.height = 0; self.btn_infinito.opacity = 0
            self.btn_eliminar_dinero.height = 0; self.btn_eliminar_dinero.opacity = 0

    def minar_monedas(self, instance):
        self.clicks_acumulados += 1
        if self.clicks_acumulados >= 2:
            datos = cargar_datos()
            datos[self.usuario_actual]["monedas"] += 1
            guardar_todos_los_datos(datos)
            self.clicks_acumulados = 0
            self.actualizar_interfaz(self.usuario_actual)

    def generar_infinito(self, instance):
        datos = cargar_datos(); datos[self.usuario_actual]["monedas"] += 1000000
        guardar_todos_los_datos(datos); self.actualizar_interfaz(self.usuario_actual)

    def vaciar_monedas(self, instance):
        datos = cargar_datos(); datos[self.usuario_actual]["monedas"] = 0
        guardar_todos_los_datos(datos); self.actualizar_interfaz(self.usuario_actual)

    def eliminar_cuenta_total(self, instance):
        datos = cargar_datos()
        if self.usuario_actual in datos:
            del datos[self.usuario_actual]
            guardar_todos_los_datos(datos)
            self.logout(None)

    def ir_a_mensajes(self, instance):
        self.manager.get_screen('mensajes').cargar_historial(self.usuario_actual)
        self.manager.current = 'mensajes'

    def transferir(self, instance):
        datos = cargar_datos(); d, c = self.dest.text.strip(), self.cant.text.strip()
        if d in datos and d != self.usuario_actual and c:
            monto = int(c)
            if datos[self.usuario_actual]["monedas"] >= monto:
                fecha = datetime.now().strftime("%d/%m %H:%M")
                datos[self.usuario_actual]["monedas"] -= monto
                datos[d]["monedas"] += monto
                datos[d].setdefault("notificaciones", []).append(f"[{fecha}] +{monto} de {self.usuario_actual}")
                guardar_todos_los_datos(datos); self.actualizar_interfaz(self.usuario_actual)
                self.dest.text = ""; self.cant.text = ""

    def logout(self, instance): self.manager.current = 'login'

class BancoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegistroScreen(name='registro'))
        sm.add_widget(BancoScreen(name='banco'))
        sm.add_widget(MensajesScreen(name='mensajes'))
        return sm

if __name__ == '__main__':
    BancoApp().run()
