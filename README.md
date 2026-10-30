# Hidra Desktop

Aplicativo gratuito de lembretes de hidratação para Windows e Linux.

O Hidra Desktop ajuda você a manter uma rotina saudável de hidratação, enviando lembretes periódicos para beber água diretamente na área de trabalho.

**Versão: 1.0.0**

## Recursos

- Interface gráfica totalmente em português.
- Intervalo de lembretes configurável.
- Duração total da sessão configurável.
- Opções para pausar, retomar e encerrar os lembretes.
- Contagem regressiva do tempo restante.
- Configurações salvas automaticamente entre execuções.
- Notificações nativas do sistema operacional.
- Compatibilidade com Windows e Linux.

## Requisitos para compilação

- Python 3.11 ou superior.
- Acesso à internet durante a instalação das dependências.
- Dependências necessárias para a plataforma escolhida.

## Compilação no Windows

1. Instale o Python 3.11 ou superior.
2. Certifique-se de que o Python esteja disponível no PATH.
3. Instale a biblioteca `winotify`, caso ela não seja instalada automaticamente pelo script.
4. Execute o arquivo `build_windows.bat`.
5. Após a compilação, o executável estará disponível em `dist/Hidra.exe`.

Para distribuir o aplicativo, copie o arquivo `dist/Hidra.exe` para a máquina de destino.

## Compilação no Linux

1. Instale o Python 3.11 ou superior.
2. Instale o suporte a ambientes virtuais (`venv`).
3. Instale o pacote `libnotify-bin`.
4. Dê permissão de execução ao script:

   ```bash
   chmod +x build_linux.sh
   ```

5. Execute o script de compilação:

   ```bash
   ./build_linux.sh
   ```

6. Após a compilação, o executável estará disponível em `dist/Hidra`.

Para distribuir o aplicativo, copie o arquivo `dist/Hidra` para a máquina de destino.

## Configurações

O Hidra Desktop salva automaticamente as preferências do usuário para preservar as configurações entre execuções.

Os arquivos de configuração são armazenados nos seguintes locais:

**Windows:**

```text
%LOCALAPPDATA%\Hidra\config.json
```

**Linux:**

```text
~/.config/hidra/config.json
```

## Notificações

O aplicativo utiliza os recursos de notificação disponíveis no sistema operacional.

**Windows:**
- As notificações dependem do suporte do Windows e das permissões de notificação do aplicativo.

**Linux:**
- É necessário utilizar uma sessão gráfica com suporte a notificações.
- Os serviços e componentes necessários devem estar instalados e funcionando na distribuição utilizada.

## Observações importantes

- Os executáveis para Windows e Linux devem ser compilados separadamente.
- Recomenda-se testar os executáveis em máquinas limpas antes da distribuição.
- O Hidra precisa permanecer em execução para emitir os lembretes.
- Pausar ou encerrar o aplicativo interrompe temporariamente ou definitivamente os lembretes da sessão.
- O aplicativo não garante o envio de notificações enquanto o computador estiver desligado ou suspenso.
- O funcionamento das notificações depende dos recursos e das configurações do sistema operacional.

## Licença

O Hidra Desktop é um software gratuito e de código aberto, distribuído sob os termos da licença MIT.

Você pode utilizar, copiar, modificar e redistribuir o aplicativo, inclusive para fins comerciais, respeitando as condições estabelecidas pela licença.

Consulte o arquivo [`LICENSE`](LICENSE) para conhecer os termos completos.

## Autor

**DevLiberator**

Projeto criado em 2026.