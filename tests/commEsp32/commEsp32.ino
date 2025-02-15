void setup() {
    Serial.begin(115200);  // Comunicação via USB (monitor serial)
    //Serial1.begin(115200, SERIAL_8N1, 16, 17);  // Configurar UART1 com TX=16 e RX=17
    Serial.println("ESP32 iniciado");
}

void loop() {
    // Enviar mensagem para a Raspberry Pi
    Serial.println("Olá, Raspberry Pi!");
    delay(1000);
    Serial.println("Aqui é a ESP32!");
    delay(1000);

    // Ler mensagem da Raspberry Pi
    if (Serial.available()) {
        String mensagem = Serial.readStringUntil('\n');
        Serial.println("Recebido: " + mensagem);  // Exibe a mensagem no monitor serial
    }
}
