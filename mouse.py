#!/usr/bin/env python3
import usb.core
import usb.util
import sys
import time

VENDOR_ID = 0x30fa
PRODUCT_ID = 0x1701

#_ws.col.info == "SET_REPORT Request"
# ==============================================================================
# СПИСОК ПАКЕТОВ НА ОТПРАВКУ (Просто перечисляйте их через запятую)
# ==============================================================================
# ==============================================================================
# ПОЛНЫЙ СПИСОК ПАКЕТОВ ПОДРЯД ИЗ ФАЙЛА DIH.TXT
# ==============================================================================
PACKETS_LIST = [






    # Блок маппинга кнопок / регистров (команда 0x10)
    [0x07, 0x10, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00],  # Кадр 341
    [0x07, 0x10, 0x02, 0x02, 0x00, 0x00, 0x00, 0x00],  # Кадр 343
    [0x07, 0x10, 0x03, 0x03, 0x00, 0x00, 0x00, 0x00],  # Кадр 345
    [0x07, 0x10, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00],  # Кадр 347
    [0x07, 0x10, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00],  # Кадр 349
    [0x07, 0x10, 0x06, 0x0c, 0x00, 0x00, 0x00, 0x00],  # Кадр 351
    [0x07, 0x10, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00],  # Кадр 353
    [0x07, 0x10, 0x08, 0x0b, 0x00, 0x00, 0x00, 0x00],  # Кадр 355
    [0x07, 0x10, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00],  # Кадр 357
    [0x07, 0x10, 0x0a, 0x00, 0x00, 0x00, 0x00, 0x00],  # Кадр 359
    [0x07, 0x10, 0x0b, 0x00, 0x00, 0x00, 0x00, 0x00],  # Кадр 361
    [0x07, 0x10, 0x0c, 0x00, 0x00, 0x00, 0x00, 0x00],  # Кадр 363
    [0x07, 0x10, 0x0d, 0x00, 0x00, 0x00, 0x00, 0x00],  # Кадр 365
    [0x07, 0x10, 0x0e, 0x00, 0x00, 0x00, 0x00, 0x00],  # Кадр 367

    [0x07, 0x12, 0x00, 0x09, 0x00, 0x00, 0x00, 0x00],  # Кадр 369

    [0x07, 0x09, 0x02, 0x48, 0x0f, 0x00, 0x00, 0x00],  # 800 синий
    [0x07, 0x09, 0x02, 0x59, 0x0f, 0x00, 0x00, 0x00],  # 1000 розовый
    [0x07, 0x09, 0x02, 0x7a, 0x0f, 0x00, 0x00, 0x00],  # красный, 1 - 200, 6 - 1200, 7 - 1400, f-4800, 
    [0x07, 0x09, 0x02, 0xab, 0x0f, 0x00, 0x00, 0x00],  # светло-фиолетовый, 2000

    [0x07, 0x13, 0x7f, 0x00, 0x00, 0x00, 0x20, 0x07],  # подсветка 6 - постоянно, 25 - всегда включена
]
# ==============================================================================
# ==============================================================================

print("Поиск мыши на USB-шине...")
dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

if dev is None:
    print("Ошибка: Мышь не найдена.")
    sys.exit(1)

detached_interfaces = []

# Принудительно освобождаем ОБА интерфейса (0 и 1), чтобы убрать Resource Busy
for interface in (0, 1):
    if dev.is_kernel_driver_active(interface):
        try:
            dev.detach_kernel_driver(interface)
            detached_interfaces.append(interface)
            print(f"Интерфейс {interface} успешно изолирован от ядра.")
        except usb.core.USBError as e:
            print(f"Предупреждение: Не удалось освободить интерфейс {interface}: {e}")

try:
    # Последовательно шлем каждый пакет из списка
    for idx, packet in enumerate(PACKETS_LIST, start=1):
        print(f"Отправка пакета {idx}/{len(PACKETS_LIST)}: {['0x{:02x}'.format(b) for b in packet]}")
        
        dev.ctrl_transfer(
            bmRequestType=0x21,  # Class / Interface
            bRequest=0x09,       # SET_REPORT
            wValue=0x0307,       # Report Type: Feature (3), ReportID: 7
            wIndex=0x0001,       # Логический wIndex: 1
            data_or_wLength=packet,
            timeout=1000
        )
        
        # Небольшая задержка между командами (50 мс), чтобы чип не захлебнулся
        if idx < len(PACKETS_LIST):
            time.sleep(0.05)
            
    print("[УСПЕХ] Все пакеты отправлены!")

except usb.core.USBError as e:
    print(f"[ОШИБКА] Мышь отвергла пакет: {e}")

finally:
    # Освобождаем ресурсы pyusb
    usb.util.dispose_resources(dev)
    
    # Возвращаем всё ядру Linux в исходное состояние
    for interface in detached_interfaces:
        try:
            dev.attach_kernel_driver(interface)
        except:
            pass
    print("Управление устройством возвращено операционной системе.")
