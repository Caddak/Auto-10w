import asyncio
import subprocess
from decky_plugin import Plugin, logger

class TDPAdjustPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.default_tdp = 15000  # TDP padrão em miliwatts (15W)
        self.low_tdp = 10000     # TDP reduzido em miliwatts (10W)
        self.is_game_running = False

    async def _main(self):
        logger.info("Iniciando monitoramento de TDP...")
        while True:
            await self.check_game_status()
            await asyncio.sleep(10)  # Verifica a cada 10 segundos

    async def _unload(self):
        logger.info("Desativando plug-in e restaurando TDP padrão...")
        self.set_tdp(self.default_tdp)

    def set_tdp(self, tdp_value):
        try:
            subprocess.run(["sudo", "ryzenadj", f"--set-tdp-limit={tdp_value}"], check=True)
            logger.info(f"TDP ajustado para {tdp_value / 1000}W")
        except Exception as e:
            logger.error(f"Erro ao ajustar TDP: {e}")

    async def check_game_status(self):
        # Verifica se há algum processo relacionado ao Steam ou jogos
        try:
            result = subprocess.run(
                ["pgrep", "-f", "steam_app_id"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            game_running = result.returncode == 0  # Retorna True se encontrar um jogo

            if game_running and not self.is_game_running:
                logger.info("Jogo detectado. Restaurando TDP padrão.")
                self.is_game_running = True
            elif not game_running and self.is_game_running:
                logger.info("Nenhum jogo detectado. Reduzindo TDP para 10W.")
                self.set_tdp(self.low_tdp)
                self.is_game_running = False
        except Exception as e:
            logger.error(f"Erro ao verificar status do jogo: {e}")

# Registro do plug-in
plugin = TDPAdjustPlugin()
