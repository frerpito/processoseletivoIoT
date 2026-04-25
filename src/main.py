from machine import Pin, ADC
import dht
import time

# ========================
# CONFIGURAÇÃO DE PINOS
# ========================

# Sensores
dht_sensor = dht.DHT22(Pin(23))
mq2 = ADC(Pin(34))
mq2.atten(ADC.ATTN_11DB)

# LEDs
led_verde = Pin(2, Pin.OUT)
led_amarelo = Pin(18, Pin.OUT)
led_vermelho = Pin(19, Pin.OUT)

# Buzzer
buzzer = Pin(21, Pin.OUT)

# ========================
# LIMITES (AJUSTÁVEIS)
# ========================

# Temperatura (°C)
TEMP_OK_MIN = 20
TEMP_OK_MAX = 26
TEMP_MOD_MIN = 16
TEMP_MOD_MAX = 30

# Umidade (%)
UMID_OK_MIN = 40
UMID_OK_MAX = 60
UMID_MOD_MIN = 30
UMID_MOD_MAX = 70

# Gás (diferença em relação ao baseline)
GAS_OK_DELTA = 100
GAS_MOD_DELTA = 300

# ========================
# VARIÁVEL DE CALIBRAÇÃO
# ========================

baseline_gas = 0

# ========================
# FUNÇÕES AUXILIARES
# ========================

def calibrar_sensor():
    global baseline_gas
    print("Calibrando sensor de gás...")
    
    soma = 0
    amostras = 10
    
    for _ in range(amostras):
        soma += mq2.read()
        time.sleep(0.2)
    
    baseline_gas = soma / amostras
    print("Baseline do gás:", baseline_gas)
    print("----------------------")

def desligar_tudo():
    led_verde.off()
    led_amarelo.off()
    led_vermelho.off()
    buzzer.off()

def avaliar_temperatura(temp):
    if TEMP_OK_MIN <= temp <= TEMP_OK_MAX:
        return "OK"
    elif TEMP_MOD_MIN <= temp <= TEMP_MOD_MAX:
        return "MODERADO"
    else:
        return "CRITICO"

def avaliar_umidade(umid):
    if UMID_OK_MIN <= umid <= UMID_OK_MAX:
        return "OK"
    elif UMID_MOD_MIN <= umid <= UMID_MOD_MAX:
        return "MODERADO"
    else:
        return "CRITICO"

def avaliar_gas(gas):
    diferenca = gas - baseline_gas

    if diferenca < GAS_OK_DELTA:
        return "OK"
    elif diferenca < GAS_MOD_DELTA:
        return "MODERADO"
    else:
        return "CRITICO"

# ========================
# SETUP INICIAL
# ========================

calibrar_sensor()

# ========================
# LOOP PRINCIPAL
# ========================

for i in range(2):
    try:
        # Leitura sensores
        dht_sensor.measure()
        temperatura = dht_sensor.temperature()
        umidade = dht_sensor.humidity()
        gas = mq2.read()

        # Avaliações individuais
        status_temp = avaliar_temperatura(temperatura)
        status_umid = avaliar_umidade(umidade)
        status_gas = avaliar_gas(gas)

        # ========================
        # DECISÃO FINAL
        # ========================

        if "CRITICO" in [status_temp, status_umid, status_gas]:
            estado = "CRITICO"

        elif "MODERADO" in [status_temp, status_umid, status_gas]:
            estado = "MODERADO"

        else:
            estado = "OK"

        # ========================
        # ATUAÇÃO
        # ========================

        desligar_tudo()

        if estado == "OK":
            led_verde.on()

        elif estado == "MODERADO":
            led_amarelo.on()

        elif estado == "CRITICO":
            led_vermelho.on()
            buzzer.on()

        # ========================
        # LOG SERIAL
        # ========================

        print("Temp:", temperatura, "°C")
        print("Umidade:", umidade, "%")
        print("Gas:", gas)
        print("Baseline:", baseline_gas)
        print("Delta Gas:", gas - baseline_gas)
        print("Estado:", estado)
        print("----------------------")

    except Exception as e:
        print("Erro na leitura:", e)

    time.sleep(2)
print("Teste")