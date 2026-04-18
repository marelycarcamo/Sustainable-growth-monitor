"""
Generador de Datos Crudos Simulados - TechNova Electronics
===========================================================
Empresa : TechNova S.R.L. — Tienda de electrónica de consumo
Período : Enero 2018 – Diciembre 2025 (8 años)
Moneda  : ARS (pesos argentinos nominales, con inflación real)

Archivos generados (datos crudos, como vendrían de los sistemas fuente):
  ventas_transacciones.csv   → Sistema POS / ERP de ventas
  compras_proveedor.csv      → Sistema de compras / costo de mercadería
  consumo_energetico.csv     → Facturas de servicios (luz, gas, solar)
  residuos_reciclaje.csv     → Registro operativo de residuos
  personal_nomina.csv        → Nómina mensual de empleados
  eventos_rrhh.csv           → Altas, bajas, accidentes, capacitaciones
  encuestas_clima.csv        → Encuestas semestrales de satisfacción

Contexto histórico simulado:
  2018-2019 : Crecimiento inicial, crisis cambiaria (dólar x2 en 2018)
  2020      : Pandemia COVID-19 — cierre total mar-may, reapertura gradual
  2021      : Rebote fuerte post-pandemia, boom tecnológico (home office)
  2022-2023 : Inflación acelerada, ajuste de precios mensual
  2024      : Estabilización relativa, mejoras ESG consolidadas
  2025      : Proyección de crecimiento con agenda verde activa
"""

import pandas as pd
import numpy as np
import os
from datetime import date, timedelta
import random

# ─── Configuración ────────────────────────────────────────────────────────────
np.random.seed(42)
random.seed(42)
OUTPUT_DIR = "technova_raw_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

INICIO = pd.Timestamp("2018-01-01")
FIN    = pd.Timestamp("2025-12-31")
meses  = pd.date_range("2018-01-01", "2025-12-31", freq="MS")  # 96 meses

# ─── Índice de inflación acumulada (base 2018=1.0, aproximación real AR) ──────
# Inflación anual aprox: 2018:48%, 2019:54%, 2020:36%, 2021:51%,
#                        2022:95%, 2023:211%, 2024:118%, 2025:45% proyectado
inflacion_anual = {
    2018: 1.00,
    2019: 1.00 * 1.48,
    2020: 1.00 * 1.48 * 1.54,
    2021: 1.00 * 1.48 * 1.54 * 1.36,
    2022: 1.00 * 1.48 * 1.54 * 1.36 * 1.51,
    2023: 1.00 * 1.48 * 1.54 * 1.36 * 1.51 * 1.95,
    2024: 1.00 * 1.48 * 1.54 * 1.36 * 1.51 * 1.95 * 3.11,
    2025: 1.00 * 1.48 * 1.54 * 1.36 * 1.51 * 1.95 * 3.11 * 2.18,
}

def infl(anio):
    return inflacion_anual[anio]

# Factor de actividad COVID por mes (0=cierre total, 1=normalidad)
covid_factor = {}
for m in meses:
    a, mo = m.year, m.month
    if   a == 2020 and mo in [3, 4, 5]:  covid_factor[m] = 0.05   # cierre ASPO
    elif a == 2020 and mo == 6:           covid_factor[m] = 0.35   # reapertura fase 1
    elif a == 2020 and mo in [7, 8]:      covid_factor[m] = 0.55
    elif a == 2020 and mo in [9, 10]:     covid_factor[m] = 0.72
    elif a == 2020 and mo in [11, 12]:    covid_factor[m] = 0.88
    elif a == 2021 and mo in [1, 2, 3]:   covid_factor[m] = 0.92   # segunda ola
    else:                                  covid_factor[m] = 1.00

# Estacionalidad electrónica (índice multiplicador mensual)
# Picos: mayo (día de la madre), julio (vacaciones), oct-nov-dic (fiestas/navidad)
estac_mes = {1:0.82, 2:0.78, 3:0.85, 4:0.90, 5:1.18, 6:0.95,
             7:1.10, 8:0.88, 9:0.92, 10:1.05, 11:1.22, 12:1.35}

# Catálogo de productos
PRODUCTOS = [
    # (id, nombre, categoria, precio_base_2018, costo_ratio)
    ("P001", "Smartphone Gama Media",    "Smartphones",    45_000, 0.62),
    ("P002", "Smartphone Gama Alta",     "Smartphones",   120_000, 0.60),
    ("P003", "Notebook 15\"",            "Computación",   180_000, 0.63),
    ("P004", "Notebook Ultra",           "Computación",   280_000, 0.61),
    ("P005", "Tablet 10\"",              "Tablets",        55_000, 0.64),
    ("P006", "Smart TV 43\"",            "TV/Audio",      110_000, 0.65),
    ("P007", "Smart TV 55\"",            "TV/Audio",      185_000, 0.63),
    ("P008", "Auriculares Bluetooth",    "Accesorios",      8_500, 0.55),
    ("P009", "Mouse Inalámbrico",        "Periféricos",     3_200, 0.50),
    ("P010", "Teclado Mecánico",         "Periféricos",    12_000, 0.52),
    ("P011", "Monitor 24\"",             "Periféricos",    55_000, 0.60),
    ("P012", "Disco SSD 1TB",            "Almacenamiento", 18_000, 0.58),
    ("P013", "Router WiFi 6",            "Redes",          15_000, 0.57),
    ("P014", "Cámara IP Seguridad",      "Seguridad",      22_000, 0.60),
    ("P015", "Servicio Técnico",         "Servicios",       5_000, 0.20),
]
prod_df = pd.DataFrame(PRODUCTOS,
    columns=["id_producto","nombre","categoria","precio_base_2018","costo_ratio"])

# Peso de ventas por producto (probabilidad relativa)
PESOS_PROD = [0.12, 0.08, 0.10, 0.05, 0.07, 0.08, 0.05,
              0.10, 0.08, 0.06, 0.06, 0.05, 0.05, 0.04, 0.01]
PESOS_PROD = np.array(PESOS_PROD) / sum(PESOS_PROD)

# Medios de pago
MEDIOS_PAGO = ["Efectivo", "Débito", "Crédito 1 cuota",
               "Crédito 3 cuotas", "Crédito 6 cuotas", "Transferencia"]
PESOS_PAGO  = [0.08, 0.22, 0.18, 0.25, 0.20, 0.07]

# Vendedores
VENDEDORES = ["V01-López", "V02-García", "V03-Martínez", "V04-Rodríguez", "V05-Fernández"]

# Proveedores
PROVEEDORES = {
    "Smartphones":    "DistribuidoraTech SA",
    "Computación":    "MegaComputo SRL",
    "Tablets":        "DistribuidoraTech SA",
    "TV/Audio":       "ElectroImport SA",
    "Accesorios":     "AccesoriosTotal SRL",
    "Periféricos":    "MegaComputo SRL",
    "Almacenamiento": "MegaComputo SRL",
    "Redes":          "NetSupply SA",
    "Seguridad":      "NetSupply SA",
    "Servicios":      "Interno",
}

# ══════════════════════════════════════════════════════════════════════════════
# 1. VENTAS_TRANSACCIONES.CSV
# Simula el sistema POS: una fila por línea de ticket
# ══════════════════════════════════════════════════════════════════════════════
print("Generando ventas_transacciones.csv ...")

filas_ventas = []
ticket_id = 10000

for mes in meses:
    a, mo = mes.year, mes.month
    factor_covid = covid_factor[mes]
    factor_estac = estac_mes[mo]
    factor_infl  = infl(a)

    # Boom 2021 post-pandemia (home office, demanda acumulada)
    factor_boom = 1.35 if a == 2021 else 1.0
    # Crecimiento real acumulado del negocio
    factor_real = 1 + 0.07 * ((a - 2018) + (mo - 1) / 12)

    # Tickets por mes (base ~280/mes en condiciones normales)
    tickets_mes = int(280 * factor_covid * factor_estac * factor_boom
                      * factor_real * np.random.normal(1, 0.06))
    tickets_mes = max(tickets_mes, 2)

    # Distribución de días hábiles en el mes
    dias_mes = pd.date_range(mes, periods=1, freq="ME")[0]
    num_dias = dias_mes.day
    dias_hab = [d for d in pd.date_range(mes, periods=num_dias)
                if d.weekday() < 6]  # lunes a sábado

    tickets_por_dia = max(1, tickets_mes // len(dias_hab))

    for dia in dias_hab:
        n_tickets = max(0, int(tickets_por_dia * np.random.normal(1, 0.25)))
        for _ in range(n_tickets):
            ticket_id += 1
            id_ticket = f"TK-{ticket_id}"
            fecha_dt  = dia + timedelta(hours=random.randint(9, 20),
                                        minutes=random.randint(0, 59))
            vendedor  = random.choices(VENDEDORES)[0]
            medio_pago = random.choices(MEDIOS_PAGO, weights=PESOS_PAGO)[0]

            # Líneas por ticket (1-3 productos)
            n_lineas = random.choices([1, 2, 3], weights=[0.70, 0.22, 0.08])[0]
            prods_ticket = np.random.choice(len(PRODUCTOS), size=n_lineas,
                                            replace=False, p=PESOS_PROD)
            for idx_p in prods_ticket:
                prod = PRODUCTOS[idx_p]
                precio_unit = prod[3] * factor_infl * np.random.normal(1, 0.03)
                cantidad    = random.choices([1, 2, 3], weights=[0.85, 0.12, 0.03])[0]
                descuento   = round(random.choices(
                    [0, 0.05, 0.10, 0.15], weights=[0.65, 0.15, 0.12, 0.08])[0], 2)
                subtotal    = round(precio_unit * cantidad * (1 - descuento), 2)

                filas_ventas.append({
                    "id_ticket":       id_ticket,
                    "fecha":           fecha_dt.strftime("%Y-%m-%d"),
                    "hora":            fecha_dt.strftime("%H:%M"),
                    "anio":            a,
                    "mes":             mo,
                    "id_producto":     prod[0],
                    "nombre_producto": prod[1],
                    "categoria":       prod[2],
                    "cantidad":        cantidad,
                    "precio_unitario": round(precio_unit, 2),
                    "descuento_pct":   descuento,
                    "subtotal_ars":    subtotal,
                    "medio_pago":      medio_pago,
                    "vendedor":        vendedor,
                    "canal":           "Local físico",
                })

df_ventas = pd.DataFrame(filas_ventas)
df_ventas.to_csv(f"{OUTPUT_DIR}/ventas_transacciones.csv", index=False)
print(f"  → {len(df_ventas):,} filas  |  {df_ventas['id_ticket'].nunique():,} tickets")


# ══════════════════════════════════════════════════════════════════════════════
# 2. COMPRAS_PROVEEDOR.CSV
# Simula órdenes de compra mensuales a proveedores
# ══════════════════════════════════════════════════════════════════════════════
print("Generando compras_proveedor.csv ...")

# Calculamos ingresos mensuales reales para derivar costo de ventas
ing_mes = df_ventas.groupby(["anio","mes"])["subtotal_ars"].sum().reset_index()
ing_mes.columns = ["anio","mes","ingresos"]

filas_compras = []
oc_id = 5000

for mes in meses:
    a, mo = mes.year, mes.month
    row = ing_mes[(ing_mes.anio == a) & (ing_mes.mes == mo)]
    ingresos_m = row["ingresos"].values[0] if len(row) else 0

    # Costo de mercadería vendida ~60% de ingresos (mejora levemente)
    cogs_ratio = 0.60 - 0.003 * ((a - 2018) + mo / 12)
    cogs_total = ingresos_m * cogs_ratio

    # Distribuir entre categorías de productos (aprox por peso)
    cats = ["Smartphones", "Computación", "Tablets", "TV/Audio",
            "Accesorios", "Periféricos", "Almacenamiento", "Redes", "Seguridad"]
    pesos_cat = [0.20, 0.22, 0.09, 0.16, 0.08, 0.10, 0.06, 0.05, 0.04]

    for cat, peso in zip(cats, pesos_cat):
        if cogs_total == 0:
            continue
        monto_cat = cogs_total * peso * np.random.normal(1, 0.08)
        if monto_cat < 100:
            continue
        oc_id += 1

        # Días de pago: entre el 5 y el 20 del mes
        dia_pago = random.randint(5, 20)
        fecha_oc = mes + pd.Timedelta(days=dia_pago - 1)

        filas_compras.append({
            "id_orden_compra": f"OC-{oc_id}",
            "fecha_emision":   mes.strftime("%Y-%m-%d"),
            "fecha_pago":      fecha_oc.strftime("%Y-%m-%d"),
            "proveedor":       PROVEEDORES[cat],
            "categoria":       cat,
            "monto_ars":       round(monto_cat, 2),
            "condicion_pago":  random.choice(["Contado", "30 días", "60 días"]),
            "estado":          "Pagado",
        })

df_compras = pd.DataFrame(filas_compras)
df_compras.to_csv(f"{OUTPUT_DIR}/compras_proveedor.csv", index=False)
print(f"  → {len(df_compras):,} filas  |  {df_compras['id_orden_compra'].nunique():,} órdenes")


# ══════════════════════════════════════════════════════════════════════════════
# 3. CONSUMO_ENERGETICO.CSV
# Simula facturas mensuales de servicios: electricidad, gas, paneles solares
# Una fila por factura/servicio por mes
# ══════════════════════════════════════════════════════════════════════════════
print("Generando consumo_energetico.csv ...")

filas_energia = []

# TechNova instala paneles solares en julio 2022 (35% de consumo cubierto)
# Amplía instalación en enero 2024 (55% de consumo cubierto)
def pct_solar(mes):
    if mes < pd.Timestamp("2022-07-01"): return 0.0
    if mes < pd.Timestamp("2024-01-01"): return 0.35
    return 0.55

for mes in meses:
    a, mo = mes.year, mes.month

    # kWh totales: base + estacionalidad (más consumo en verano por A/C y en invierno por calefacción)
    kwh_base = 7_800  # kWh base mensual (iluminación, equipos, A/C)
    factor_estac_e = 1 + 0.20 * abs(np.sin(np.pi * mo / 12))  # picos en ene y dic
    factor_act  = covid_factor[mes] * 0.6 + 0.4              # local semi-cerrado igual consume base
    factor_efic = 0.97 ** (a - 2018 + (mo - 1) / 12)         # mejora eficiencia 3%/año (LED, HVAC)
    factor_boom = 1.08 if a == 2021 else 1.0                  # más actividad 2021

    kwh_total = (kwh_base * factor_estac_e * factor_act
                 * factor_efic * factor_boom * np.random.normal(1, 0.04))

    solar_ratio = pct_solar(mes)
    kwh_solar   = kwh_total * solar_ratio
    kwh_red     = kwh_total * (1 - solar_ratio)

    # Tarifa eléctrica evoluciona con inflación (más subsidio hasta 2023, luego liberación)
    tarifa_base = 12.5  # ARS/kWh en 2018
    factor_tarifa = {2018:1.0, 2019:1.6, 2020:1.8, 2021:2.0,
                     2022:2.8, 2023:6.5, 2024:18.0, 2025:28.0}
    tarifa = tarifa_base * factor_tarifa[a] * np.random.normal(1, 0.02)

    monto_electricidad = kwh_red * tarifa

    # Gas (calefacción y agua caliente) — más en invierno
    m3_gas = 0
    monto_gas = 0
    if mo in [5, 6, 7, 8, 9]:  # temporada gas
        m3_gas = (280 + 60 * np.sin(np.pi * (mo - 4) / 5)) * np.random.normal(1, 0.08)
        tarifa_gas_base = 8.0  # ARS/m3 en 2018
        tarifa_gas = tarifa_gas_base * factor_tarifa[a] * np.random.normal(1, 0.02)
        monto_gas  = m3_gas * tarifa_gas

    # Factura electricidad
    filas_energia.append({
        "id_factura":      f"FAC-E-{a}{mo:02d}",
        "fecha":           mes.strftime("%Y-%m-%d"),
        "anio":            a,
        "mes":             mo,
        "tipo_servicio":   "Electricidad Red",
        "proveedor":       "EDENOR",
        "kwh_consumidos":  round(kwh_red, 1),
        "kwh_generados":   0,
        "m3_gas":          0,
        "tarifa_unitaria": round(tarifa, 4),
        "monto_ars":       round(monto_electricidad, 2),
        "es_renovable":    False,
    })

    # Factura gas (solo meses fríos)
    if monto_gas > 0:
        filas_energia.append({
            "id_factura":      f"FAC-G-{a}{mo:02d}",
            "fecha":           mes.strftime("%Y-%m-%d"),
            "anio":            a,
            "mes":             mo,
            "tipo_servicio":   "Gas Natural",
            "proveedor":       "Metrogas",
            "kwh_consumidos":  0,
            "kwh_generados":   0,
            "m3_gas":          round(m3_gas, 1),
            "tarifa_unitaria": round(tarifa_gas, 4),
            "monto_ars":       round(monto_gas, 2),
            "es_renovable":    False,
        })

    # Producción solar (desde julio 2022)
    if kwh_solar > 0:
        filas_energia.append({
            "id_factura":      f"FAC-S-{a}{mo:02d}",
            "fecha":           mes.strftime("%Y-%m-%d"),
            "anio":            a,
            "mes":             mo,
            "tipo_servicio":   "Panel Solar",
            "proveedor":       "Autoconsumo",
            "kwh_consumidos":  round(kwh_solar, 1),
            "kwh_generados":   round(kwh_solar, 1),
            "m3_gas":          0,
            "tarifa_unitaria": 0,
            "monto_ars":       0,
            "es_renovable":    True,
        })

df_energia = pd.DataFrame(filas_energia)
df_energia.to_csv(f"{OUTPUT_DIR}/consumo_energetico.csv", index=False)
print(f"  → {len(df_energia):,} filas  |  tipos: {df_energia['tipo_servicio'].unique().tolist()}")


# ══════════════════════════════════════════════════════════════════════════════
# 4. RESIDUOS_RECICLAJE.CSV
# Registro semanal del operador de logística
# ══════════════════════════════════════════════════════════════════════════════
print("Generando residuos_reciclaje.csv ...")

filas_residuos = []
reg_id = 1000

# TechNova firma convenio de reciclaje de e-waste en abril 2020
# Amplía programa en enero 2023 (incluye embalajes y pilas)
def tasa_reciclaje_esperada(mes):
    if mes < pd.Timestamp("2020-04-01"): return 0.18
    if mes < pd.Timestamp("2023-01-01"): return 0.42
    return 0.65

TIPOS_RESIDUO = [
    # (tipo, descripcion, kg_base_mensual, reciclable_base)
    ("Embalaje cartón",    "Cajas y embalajes de productos",     95,  True),
    ("Plástico",           "Film, espumas y plásticos varios",   38,  False),
    ("E-waste",            "Componentes y productos defectuosos",22,  True),
    ("Pilas y baterías",   "Pilas agotadas y baterías de litio", 8,   True),
    ("Residuo general",    "Residuos de oficina y comedor",      30,  False),
    ("Papel y cartón of.", "Papel de impresión y documentos",    12,  True),
]

semanas = pd.date_range("2018-01-01", "2025-12-31", freq="W-MON")

for semana in semanas:
    a, mo = semana.year, semana.month
    if semana > FIN:
        break

    factor_act   = covid_factor.get(semana.replace(day=1), 1.0)
    factor_vol   = 1 + 0.04 * (a - 2018)           # más actividad con el tiempo
    tasa_rec_esp = tasa_reciclaje_esperada(semana)

    for tipo, desc, kg_base, es_rec_base in TIPOS_RESIDUO:
        kg_generado = max(0.5, (kg_base / 4) * factor_act * factor_vol
                          * np.random.normal(1, 0.15))

        # Reciclado: depende si el tipo es reciclable y el programa vigente
        if es_rec_base:
            kg_reciclado = kg_generado * tasa_rec_esp * np.random.normal(1, 0.10)
        else:
            # Residuos no reciclables: pequeño porcentaje igual va a reciclaje tras 2023
            kg_reciclado = kg_generado * (tasa_rec_esp * 0.2 if semana >= pd.Timestamp("2023-01-01") else 0)

        kg_reciclado = min(kg_reciclado, kg_generado)

        filas_residuos.append({
            "id_registro":      f"RES-{reg_id:06d}",
            "fecha_semana":     semana.strftime("%Y-%m-%d"),
            "anio":             a,
            "mes":              mo,
            "tipo_residuo":     tipo,
            "descripcion":      desc,
            "kg_generados":     round(kg_generado, 2),
            "kg_reciclados":    round(kg_reciclado, 2),
            "kg_disposicion":   round(kg_generado - kg_reciclado, 2),
            "operador_retiro":  random.choice(["EcoRetiro SA", "VerdeLogística", "Municipal"]),
        })
        reg_id += 1

df_residuos = pd.DataFrame(filas_residuos)
df_residuos.to_csv(f"{OUTPUT_DIR}/residuos_reciclaje.csv", index=False)
print(f"  → {len(df_residuos):,} filas  |  tipos: {df_residuos['tipo_residuo'].nunique()} tipos de residuo")


# ══════════════════════════════════════════════════════════════════════════════
# 5. PERSONAL_NOMINA.CSV
# Estado mensual de la nómina (snapshot por mes)
# ══════════════════════════════════════════════════════════════════════════════
print("Generando personal_nomina.csv ...")

# Empleados base al inicio (2018)
EMPLEADOS_INICIALES = [
    # (id, nombre, puesto, area, genero, salario_base_2018, fecha_ingreso)
    ("E001","Fernández, Carlos",  "Gerente General",       "Administración", "M", 85_000, "2018-01-01"),
    ("E002","López, María",       "Jefe de Ventas",        "Ventas",         "F", 55_000, "2018-01-01"),
    ("E003","García, Juan",       "Vendedor Senior",       "Ventas",         "M", 38_000, "2018-01-01"),
    ("E004","Martínez, Ana",      "Vendedora",             "Ventas",         "F", 32_000, "2018-01-01"),
    ("E005","Rodríguez, Luis",    "Técnico Senior",        "Taller",         "M", 42_000, "2018-01-01"),
    ("E006","Sánchez, Pablo",     "Técnico",               "Taller",         "M", 34_000, "2018-01-01"),
    ("E007","Torres, Sofía",      "Administrativa",        "Administración", "F", 33_000, "2018-01-01"),
    ("E008","Ramírez, Diego",     "Encargado Depósito",    "Logística",      "M", 36_000, "2018-01-01"),
    ("E009","Flores, Valeria",    "Vendedora",             "Ventas",         "F", 30_000, "2018-01-01"),
    ("E010","Medina, Roberto",    "Técnico",               "Taller",         "M", 32_000, "2018-03-01"),
]

# Altas y bajas programadas (fecha, tipo, datos)
MOVIMIENTOS = [
    # Año 2019
    ("2019-03-01", "alta",  "E011","Jiménez, Laura",   "Vendedora",       "Ventas",         "F", 33_000),
    ("2019-07-01", "alta",  "E012","Peralta, Marcos",  "Vendedor",        "Ventas",         "M", 33_000),
    ("2019-10-01", "baja",  "E009","baja voluntaria",  "", "", "", 0),
    # Año 2020 (pandemia — no hay nuevas incorporaciones hasta fines de año)
    ("2020-03-01", "baja",  "E012","suspensión ATP",   "", "", "", 0),  # suspendido, vuelve en sep
    ("2020-09-01", "alta",  "E012","Peralta, Marcos",  "Vendedor",        "Ventas",         "M", 36_000),
    ("2020-11-01", "alta",  "E013","Castro, Luciana",  "Administrativa",  "Administración", "F", 35_000),
    # Año 2021 (boom — crecimiento del equipo)
    ("2021-02-01", "alta",  "E014","Ruiz, Nicolás",    "Técnico",         "Taller",         "M", 42_000),
    ("2021-04-01", "alta",  "E015","Morales, Camila",  "Vendedora",       "Ventas",         "F", 38_000),
    ("2021-06-01", "alta",  "E016","Vargas, Hernán",   "Depósito",        "Logística",      "M", 36_000),
    ("2021-08-01", "baja",  "E006","baja voluntaria",  "", "", "", 0),
    ("2021-09-01", "alta",  "E017","Acosta, Florencia","Técnica",         "Taller",         "F", 42_000),
    # Año 2022
    ("2022-01-01", "alta",  "E018","Ibáñez, Tomás",    "Vendedor",        "Ventas",         "M", 50_000),
    ("2022-05-01", "baja",  "E011","baja voluntaria",  "", "", "", 0),
    ("2022-07-01", "alta",  "E019","Suárez, Beatriz",  "Contadora",       "Administración", "F", 75_000),
    # Año 2023
    ("2023-01-01", "alta",  "E020","Ríos, Agustín",    "Técnico ESG",     "Administración", "M", 90_000),
    ("2023-04-01", "baja",  "E010","jubilación",       "", "", "", 0),
    ("2023-06-01", "alta",  "E021","Mendoza, Sofía",   "Técnica",         "Taller",         "F", 65_000),
    # Año 2024
    ("2024-02-01", "alta",  "E022","Herrera, Matías",  "Vendedor",        "Ventas",         "M", 150_000),
    ("2024-03-01", "baja",  "E003","retiro voluntario","", "", "", 0),
    ("2024-08-01", "alta",  "E023","Quiroga, Julia",   "Depósito",        "Logística",      "F", 140_000),
    # Año 2025
    ("2025-01-01", "alta",  "E024","Navarro, Leandro", "IT / BI",         "Administración", "M", 280_000),
    ("2025-03-01", "baja",  "E008","baja voluntaria",  "", "", "", 0),
    ("2025-06-01", "alta",  "E025","Paz, Valentina",   "Vendedora",       "Ventas",         "F", 260_000),
]

# Construir estado de nómina mes a mes
empleados_activos = {e[0]: {
    "id": e[0], "nombre": e[1], "puesto": e[2], "area": e[3],
    "genero": e[4], "salario_base": e[5], "fecha_ingreso": e[6]
} for e in EMPLEADOS_INICIALES}

filas_nomina = []

for mes in meses:
    mes_str = mes.strftime("%Y-%m-%d")

    # Procesar movimientos de este mes
    for mov in MOVIMIENTOS:
        if mov[0] == mes_str:
            if mov[1] == "alta":
                empleados_activos[mov[2]] = {
                    "id": mov[2], "nombre": mov[3], "puesto": mov[4],
                    "area": mov[5], "genero": mov[6],
                    "salario_base": mov[7], "fecha_ingreso": mes_str
                }
            elif mov[1] == "baja" and mov[2] in empleados_activos:
                del empleados_activos[mov[2]]

    a = mes.year
    # Ajuste salarial por inflación (paritarias anuales en marzo, más bono dic)
    factor_sal = inflacion_anual[a] / inflacion_anual[2018]

    for eid, emp in empleados_activos.items():
        sal_nominal = emp["salario_base"] * factor_sal * np.random.normal(1, 0.01)
        bono = sal_nominal * 0.5 if mes.month == 12 else 0  # aguinaldo dic

        filas_nomina.append({
            "id_empleado":     eid,
            "nombre":          emp["nombre"],
            "mes":             mes_str,
            "anio":            mes.year,
            "mes_num":         mes.month,
            "puesto":          emp["puesto"],
            "area":            emp["area"],
            "genero":          emp["genero"],
            "fecha_ingreso":   emp["fecha_ingreso"],
            "salario_nominal": round(sal_nominal, 2),
            "bono_dic":        round(bono, 2),
            "total_devengado": round(sal_nominal + bono, 2),
        })

df_nomina = pd.DataFrame(filas_nomina)
df_nomina.to_csv(f"{OUTPUT_DIR}/personal_nomina.csv", index=False)
print(f"  → {len(df_nomina):,} filas  |  pico empleados: {df_nomina.groupby('mes')['id_empleado'].count().max()}")


# ══════════════════════════════════════════════════════════════════════════════
# 6. EVENTOS_RRHH.CSV
# Registro de eventos individuales: accidentes, capacitaciones, sanciones
# ══════════════════════════════════════════════════════════════════════════════
print("Generando eventos_rrhh.csv ...")

filas_eventos = []
ev_id = 1

for mes in meses:
    a, mo = mes.year, mes.month
    mes_str = mes.strftime("%Y-%m-%d")

    # Empleados activos en este mes (simplificado)
    emp_activos_mes = df_nomina[
        (df_nomina.anio == a) & (df_nomina.mes_num == mo)
    ]["id_empleado"].tolist()

    n_emp = len(emp_activos_mes)
    if n_emp == 0:
        continue

    # Accidentes laborales (Poisson, mejora con el tiempo)
    lambda_acc = max(0.1, 0.6 - 0.04 * (a - 2018))
    n_accidentes = np.random.poisson(lambda_acc)
    for _ in range(n_accidentes):
        dia = random.randint(1, 28)
        filas_eventos.append({
            "id_evento":    f"EV-{ev_id:05d}",
            "fecha":        f"{a}-{mo:02d}-{dia:02d}",
            "anio":         a, "mes": mo,
            "id_empleado":  random.choice(emp_activos_mes),
            "tipo_evento":  "Accidente Laboral",
            "descripcion":  random.choice([
                "Corte leve manipulando embalaje",
                "Caída leve en depósito",
                "Lesión lumbar por carga",
                "Golpe con estantería",
            ]),
            "dias_baja":    random.choice([1, 2, 3, 5, 7]),
            "horas_capacitacion": 0,
            "area":         random.choice(["Logística", "Taller"]),
        })
        ev_id += 1

    # Capacitaciones (más frecuentes desde 2021)
    base_cap = 1.5 if a >= 2021 else 0.8
    if a >= 2023:
        base_cap = 2.5  # programa ESG
    n_caps = np.random.poisson(base_cap * n_emp / 5)
    for _ in range(n_caps):
        dia = random.randint(1, 28)
        tipo_cap = random.choice([
            "Atención al cliente", "Productos nuevos", "Seguridad laboral",
            "ESG y sostenibilidad", "Excel / herramientas", "Técnico especialización"
        ])
        filas_eventos.append({
            "id_evento":    f"EV-{ev_id:05d}",
            "fecha":        f"{a}-{mo:02d}-{dia:02d}",
            "anio":         a, "mes": mo,
            "id_empleado":  random.choice(emp_activos_mes),
            "tipo_evento":  "Capacitación",
            "descripcion":  tipo_cap,
            "dias_baja":    0,
            "horas_capacitacion": random.choice([4, 8, 16, 24]),
            "area":         "Todas",
        })
        ev_id += 1

df_eventos = pd.DataFrame(filas_eventos)
df_eventos.to_csv(f"{OUTPUT_DIR}/eventos_rrhh.csv", index=False)
print(f"  → {len(df_eventos):,} filas  |  accidentes: {(df_eventos.tipo_evento=='Accidente Laboral').sum()}  |  capacitaciones: {(df_eventos.tipo_evento=='Capacitación').sum()}")


# ══════════════════════════════════════════════════════════════════════════════
# 7. ENCUESTAS_CLIMA.CSV
# Encuesta semestral de satisfacción laboral (junio y diciembre)
# ══════════════════════════════════════════════════════════════════════════════
print("Generando encuestas_clima.csv ...")

filas_encuestas = []

for mes in meses:
    if mes.month not in [6, 12]:
        continue
    a, mo = mes.year, mes.month

    emp_mes = df_nomina[
        (df_nomina.anio == a) & (df_nomina.mes_num == mo)
    ][["id_empleado","nombre","area","genero"]].copy()

    # Tasa de respuesta (mejora con años)
    tasa_resp = min(0.95, 0.70 + 0.03 * (a - 2018))
    emp_respondentes = emp_mes.sample(frac=tasa_resp, random_state=a * 10 + mo)

    # Puntaje base mejora levemente; baja en pandemia y en picos inflación
    base_satisf = 6.8
    if a == 2020: base_satisf -= 1.2
    if a == 2023: base_satisf -= 0.5   # estrés por inflación
    base_satisf += 0.12 * (a - 2018)
    base_satisf = min(base_satisf, 9.2)

    for _, emp in emp_respondentes.iterrows():
        ruido = np.random.normal(0, 0.8)
        puntaje = round(np.clip(base_satisf + ruido, 1, 10), 1)

        filas_encuestas.append({
            "id_respuesta":      f"ENC-{a}{mo:02d}-{emp['id_empleado']}",
            "fecha_encuesta":    mes.strftime("%Y-%m-%d"),
            "anio":              a,
            "semestre":          1 if mo == 6 else 2,
            "id_empleado":       emp["id_empleado"],
            "area":              emp["area"],
            "genero":            emp["genero"],
            "satisfaccion_gral": puntaje,
            "clima_equipo":      round(np.clip(puntaje + np.random.normal(0, 0.5), 1, 10), 1),
            "liderazgo":         round(np.clip(puntaje + np.random.normal(0, 0.6), 1, 10), 1),
            "condiciones_fisicas": round(np.clip(puntaje + np.random.normal(0.3, 0.4), 1, 10), 1),
            "recomendaria_empresa": "Sí" if puntaje >= 7 else ("Tal vez" if puntaje >= 5 else "No"),
        })

df_encuestas = pd.DataFrame(filas_encuestas)
df_encuestas.to_csv(f"{OUTPUT_DIR}/encuestas_clima.csv", index=False)
print(f"  → {len(df_encuestas):,} filas  |  {df_encuestas[['anio','semestre']].drop_duplicates().shape[0]} períodos encuestados")


# ══════════════════════════════════════════════════════════════════════════════
# RESUMEN FINAL
# ══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 62)
print("  TechNova Electronics — Datos Crudos Generados")
print("=" * 62)
archivos = [
    ("ventas_transacciones.csv", df_ventas),
    ("compras_proveedor.csv",    df_compras),
    ("consumo_energetico.csv",   df_energia),
    ("residuos_reciclaje.csv",   df_residuos),
    ("personal_nomina.csv",      df_nomina),
    ("eventos_rrhh.csv",         df_eventos),
    ("encuestas_clima.csv",      df_encuestas),
]
total = 0
for nombre, df in archivos:
    print(f"  {nombre:<35} {len(df):>7,} filas")
    total += len(df)
print(f"  {'─'*50}")
print(f"  {'TOTAL':<35} {total:>7,} filas")
print("=" * 62)
print(f"\n  Período: Ene 2018 → Dic 2025  ({len(meses)} meses)")
print(f"  Archivos en: ./{OUTPUT_DIR}/")
print()
print("  Eventos históricos simulados:")
print("  2018     Crisis cambiaria (inflación +48%)")
print("  2020     Pandemia — cierre total mar-may")
print("  2021     Boom tecnológico post-pandemia")
print("  2022 jul Instalación paneles solares (35% cobertura)")
print("  2023     Hiperinflación — ajuste precios mensual")
print("  2023 ene Programa ampliado de reciclaje (e-waste + pilas)")
print("  2024 ene Ampliación solar (55% cobertura)")
print("  2025     Proyección con agenda verde activa")
