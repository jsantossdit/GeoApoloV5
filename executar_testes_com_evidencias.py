#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Executor de Testes Automatizados com Geração de Evidências.
Gera relatórios em HTML moderno, Markdown e Log na pasta do executável (GeoAlvo.exe).
"""

import sys
import os
import time
import datetime
import platform
import unittest
import traceback
import argparse
from typing import List, Dict, Any, Optional

# Garantir que a raiz do projeto esteja no sys.path
PASTA_RAIZ = os.path.abspath(os.path.dirname(__file__))
if PASTA_RAIZ not in sys.path:
    sys.path.insert(0, PASTA_RAIZ)


class CasoTesteEvidencia:
    """Armazena informações individuais de cada caso de teste executado."""

    def __init__(self, test_id: str, nome: str, modulo: str, classe: str, docstring: str = ""):
        self.test_id = test_id
        self.nome = nome
        self.modulo = modulo
        self.classe = classe
        self.docstring = (docstring or "").strip()
        self.status = "PENDENTE"  # SUCESSO, FALHA, ERRO, IGNORADO
        self.tempo_execucao: float = 0.0
        self.mensagem_erro: str = ""
        self.traceback_erro: str = ""

    def para_dicionario(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "nome": self.nome,
            "modulo": self.modulo,
            "classe": self.classe,
            "docstring": self.docstring,
            "status": self.status,
            "tempo_execucao": round(self.tempo_execucao, 4),
            "mensagem_erro": self.mensagem_erro,
            "traceback_erro": self.traceback_erro,
        }


class ColetorEvidenciasTestResult(unittest.TestResult):
    """Custom TestResult para capturar detalhadamente cada teste."""

    def __init__(self, stream=None, descriptions=None, verbosity=1):
        super().__init__(stream=stream, descriptions=descriptions, verbosity=verbosity)
        self.evidencias: List[CasoTesteEvidencia] = []
        self._teste_atual: Optional[CasoTesteEvidencia] = None
        self._tempo_inicio_teste: float = 0.0
        self.tempo_inicio_total: float = time.time()
        self.tempo_fim_total: float = 0.0

    def startTest(self, test):
        super().startTest(test)
        self._tempo_inicio_teste = time.time()
        test_id = test.id()
        partes = test_id.split(".")
        if len(partes) >= 4:
            modulo = partes[1]
            classe = partes[-2]
            nome = partes[-1]
        elif len(partes) == 3:
            modulo = partes[0]
            classe = partes[1]
            nome = partes[2]
        elif len(partes) == 2:
            modulo = partes[0]
            classe = ""
            nome = partes[1]
        else:
            modulo = ""
            classe = ""
            nome = test_id
        docstring = test._testMethodDoc if hasattr(test, "_testMethodDoc") else ""

        self._teste_atual = CasoTesteEvidencia(
            test_id=test_id,
            nome=nome,
            modulo=modulo,
            classe=classe,
            docstring=docstring or "",
        )
        self.evidencias.append(self._teste_atual)

    def stopTest(self, test):
        super().stopTest(test)
        if self._teste_atual:
            self._teste_atual.tempo_execucao = time.time() - self._tempo_inicio_teste

    def addSuccess(self, test):
        super().addSuccess(test)
        if self._teste_atual:
            self._teste_atual.status = "SUCESSO"

    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self._teste_atual:
            self._teste_atual.status = "FALHA"
            exctype, value, tb = err
            self._teste_atual.mensagem_erro = str(value)
            self._teste_atual.traceback_erro = "".join(traceback.format_exception(exctype, value, tb))

    def addError(self, test, err):
        super().addError(test, err)
        if self._teste_atual:
            self._teste_atual.status = "ERRO"
            exctype, value, tb = err
            self._teste_atual.mensagem_erro = str(value)
            self._teste_atual.traceback_erro = "".join(traceback.format_exception(exctype, value, tb))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self._teste_atual:
            self._teste_atual.status = "IGNORADO"
            self._teste_atual.mensagem_erro = reason

    def consolidar_metricas(self) -> Dict[str, Any]:
        self.tempo_fim_total = time.time()
        duracao = self.tempo_fim_total - self.tempo_inicio_total

        total = len(self.evidencias)
        sucessos = sum(1 for e in self.evidencias if e.status == "SUCESSO")
        falhas = sum(1 for e in self.evidencias if e.status == "FALHA")
        erros = sum(1 for e in self.evidencias if e.status == "ERRO")
        ignorados = sum(1 for e in self.evidencias if e.status == "IGNORADO")
        taxa_sucesso = (sucessos / total * 100.0) if total > 0 else 0.0

        return {
            "total": total,
            "sucessos": sucessos,
            "falhas": falhas,
            "erros": erros,
            "ignorados": ignorados,
            "taxa_sucesso": round(taxa_sucesso, 2),
            "duracao_segundos": round(duracao, 2),
            "data_hora": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "timestamp_iso": datetime.datetime.now().isoformat(),
            "sistema_operacional": platform.platform(),
            "python_versao": platform.python_version(),
            "arquitetura": platform.architecture()[0],
            "evidencias": [e.para_dicionario() for e in self.evidencias],
        }


class GeradorRelatorioEvidencias:
    """Gera arquivos de evidência em HTML, Markdown e Log."""

    @staticmethod
    def gerar_html(dados: Dict[str, Any], caminho_arquivo: str) -> None:
        """Gera um arquivo HTML completo, autônomo (sem dependência externa de internet)."""
        taxa = dados["taxa_sucesso"]
        cor_taxa = "#2E7D32" if taxa >= 95.0 else ("#F57F17" if taxa >= 80.0 else "#C62828")
        cor_status_geral = "#2E7D32" if (dados["falhas"] == 0 and dados["erros"] == 0) else "#C62828"
        texto_status_geral = "APROVADO" if (dados["falhas"] == 0 and dados["erros"] == 0) else "REPROVADO"

        linhas_tabela = []
        for i, ev in enumerate(dados["evidencias"], 1):
            st = ev["status"]
            if st == "SUCESSO":
                badge = '<span class="badge badge-success">APROVADO</span>'
                tr_class = "row-pass"
            elif st == "FALHA":
                badge = '<span class="badge badge-fail">FALHA</span>'
                tr_class = "row-fail"
            elif st == "ERRO":
                badge = '<span class="badge badge-error">ERRO</span>'
                tr_class = "row-error"
            else:
                badge = '<span class="badge badge-skip">IGNORADO</span>'
                tr_class = "row-skip"

            detalhes_html = ""
            if ev["traceback_erro"]:
                escaped_tb = (
                    ev["traceback_erro"]
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                detalhes_html = f"""
                <details class="tb-details">
                    <summary>Ver Detalhes do Erro</summary>
                    <pre><code>{escaped_tb}</code></pre>
                </details>
                """
            elif ev["mensagem_erro"]:
                escaped_msg = (
                    ev["mensagem_erro"]
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                detalhes_html = f"""<div class="msg-skip"><em>{escaped_msg}</em></div>"""

            doc_text = f"<br><small class='text-muted'>{ev['docstring']}</small>" if ev["docstring"] else ""

            linhas_tabela.append(f"""
            <tr class="{tr_class}">
                <td style="text-align: center;">{i}</td>
                <td><code>{ev['modulo']}</code></td>
                <td><strong>{ev['classe']}</strong></td>
                <td><strong>{ev['nome']}</strong>{doc_text}{detalhes_html}</td>
                <td style="text-align: right;">{ev['tempo_execucao'] * 1000:.1f} ms</td>
                <td style="text-align: center;">{badge}</td>
            </tr>
            """)

        html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evidência de Testes Automatizados - GeoAlvo</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background-color: #F8FAFC; color: #1E293B; padding: 24px; line-height: 1.5; }}
        .container {{ max-width: 1300px; margin: 0 auto; }}
        header {{ background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); color: #FFFFFF; padding: 28px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; }}
        header h1 {{ font-size: 24px; font-weight: 700; }}
        header p {{ color: #94A3B8; font-size: 14px; margin-top: 4px; }}
        .header-badge {{ background-color: {cor_status_geral}; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 16px; letter-spacing: 0.5px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .card {{ background: white; padding: 18px; border-radius: 10px; border: 1px solid #E2E8F0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        .card-label {{ font-size: 12px; font-weight: 600; text-transform: uppercase; color: #64748B; margin-bottom: 6px; }}
        .card-value {{ font-size: 26px; font-weight: 700; color: #0F172A; }}
        .card-value.pass {{ color: #16A34A; }}
        .card-value.fail {{ color: #DC2626; }}
        .card-value.error {{ color: #EA580C; }}
        .card-value.skip {{ color: #64748B; }}
        .card-value.rate {{ color: {cor_taxa}; }}
        
        .info-panel {{ background: white; padding: 16px 20px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 24px; font-size: 13px; color: #475569; display: flex; flex-wrap: wrap; gap: 24px; }}
        .info-item strong {{ color: #0F172A; }}

        .table-controls {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 12px; }}
        .search-box {{ padding: 8px 14px; border: 1px solid #CBD5E1; border-radius: 6px; font-size: 14px; width: 300px; }}
        .filter-buttons {{ display: flex; gap: 8px; }}
        .btn-filter {{ background: white; border: 1px solid #CBD5E1; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; transition: all 0.2s; }}
        .btn-filter:hover, .btn-filter.active {{ background: #1E3A8A; color: white; border-color: #1E3A8A; }}

        .table-responsive {{ background: white; border-radius: 10px; border: 1px solid #E2E8F0; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }}
        th {{ background-color: #F1F5F9; color: #334155; font-weight: 600; padding: 12px 14px; border-bottom: 1px solid #E2E8F0; }}
        td {{ padding: 12px 14px; border-bottom: 1px solid #F1F5F9; vertical-align: top; }}
        tr:last-child td {{ border-bottom: none; }}
        tr.row-fail {{ background-color: #FEF2F2; }}
        tr.row-error {{ background-color: #FFF7ED; }}
        
        .badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; }}
        .badge-success {{ background-color: #DCFCE7; color: #166534; }}
        .badge-fail {{ background-color: #FEE2E2; color: #991B1B; }}
        .badge-error {{ background-color: #FFEDD5; color: #9A3412; }}
        .badge-skip {{ background-color: #F1F5F9; color: #475569; }}
        
        .text-muted {{ color: #64748B; }}
        .msg-skip {{ margin-top: 4px; color: #64748B; font-size: 12px; }}
        .tb-details {{ margin-top: 6px; }}
        .tb-details summary {{ cursor: pointer; color: #DC2626; font-weight: 600; font-size: 12px; }}
        .tb-details pre {{ background: #0F172A; color: #F8FAFC; padding: 10px; border-radius: 6px; font-size: 11px; overflow-x: auto; margin-top: 6px; white-space: pre-wrap; }}
        
        footer {{ text-align: center; margin-top: 32px; font-size: 12px; color: #94A3B8; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🛡️ Relatório de Evidências de Testes Automatizados</h1>
                <p>Ambiente: GeoAlvo / GeoApolo V5 &bull; Executável Oficial: GeoAlvo.exe</p>
            </div>
            <div class="header-badge">{texto_status_geral}</div>
        </header>

        <div class="metrics-grid">
            <div class="card">
                <div class="card-label">Total de Testes</div>
                <div class="card-value">{dados['total']}</div>
            </div>
            <div class="card">
                <div class="card-label">Aprovados</div>
                <div class="card-value pass">{dados['sucessos']}</div>
            </div>
            <div class="card">
                <div class="card-label">Falhas</div>
                <div class="card-value fail">{dados['falhas']}</div>
            </div>
            <div class="card">
                <div class="card-label">Erros</div>
                <div class="card-value error">{dados['erros']}</div>
            </div>
            <div class="card">
                <div class="card-label">Ignorados</div>
                <div class="card-value skip">{dados['ignorados']}</div>
            </div>
            <div class="card">
                <div class="card-label">Taxa de Sucesso</div>
                <div class="card-value rate">{dados['taxa_sucesso']}%</div>
            </div>
            <div class="card">
                <div class="card-label">Duração Total</div>
                <div class="card-value">{dados['duracao_segundos']}s</div>
            </div>
        </div>

        <div class="info-panel">
            <div class="info-item"><strong>Data e Hora:</strong> {dados['data_hora']}</div>
            <div class="info-item"><strong>Sistema Operacional:</strong> {dados['sistema_operacional']}</div>
            <div class="info-item"><strong>Python:</strong> {dados['python_versao']} ({dados['arquitetura']})</div>
            <div class="info-item"><strong>Local do Relatório:</strong> {os.path.abspath(caminho_arquivo)}</div>
        </div>

        <div class="table-controls">
            <input type="text" id="filtroTexto" class="search-box" placeholder="🔍 Filtrar por teste, classe ou módulo..." onkeyup="filtrarTabela()">
            <div class="filter-buttons">
                <button class="btn-filter active" onclick="filtrarStatus('TODOS', this)">Todos ({dados['total']})</button>
                <button class="btn-filter" onclick="filtrarStatus('APROVADO', this)">Aprovados ({dados['sucessos']})</button>
                <button class="btn-filter" onclick="filtrarStatus('FALHA', this)">Falhas ({dados['falhas']})</button>
                <button class="btn-filter" onclick="filtrarStatus('ERRO', this)">Erros ({dados['erros']})</button>
                <button class="btn-filter" onclick="filtrarStatus('IGNORADO', this)">Ignorados ({dados['ignorados']})</button>
            </div>
        </div>

        <div class="table-responsive">
            <table id="tabelaTestes">
                <thead>
                    <tr>
                        <th style="width: 50px; text-align: center;">#</th>
                        <th style="width: 150px;">Módulo</th>
                        <th style="width: 200px;">Classe</th>
                        <th>Caso de Teste / Detalhes</th>
                        <th style="width: 100px; text-align: right;">Duração</th>
                        <th style="width: 110px; text-align: center;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(linhas_tabela)}
                </tbody>
            </table>
        </div>

        <footer>
            GeoAlvo Suite &bull; Gerado automaticamente em {dados['data_hora']} &bull; Evidência oficial de qualidade de software
        </footer>
    </div>

    <script>
        let statusAtual = 'TODOS';

        function filtrarStatus(status, btn) {{
            statusAtual = status;
            document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filtrarTabela();
        }}

        function filtrarTabela() {{
            const input = document.getElementById('filtroTexto');
            const termo = input.value.toLowerCase();
            const linhas = document.querySelectorAll('#tabelaTestes tbody tr');

            linhas.forEach(linha => {{
                const textoLinha = linha.innerText.toLowerCase();
                const correspondeTexto = textoLinha.includes(termo);

                let correspondeStatus = true;
                if (statusAtual === 'APROVADO') correspondeStatus = linha.classList.contains('row-pass');
                else if (statusAtual === 'FALHA') correspondeStatus = linha.classList.contains('row-fail');
                else if (statusAtual === 'ERRO') correspondeStatus = linha.classList.contains('row-error');
                else if (statusAtual === 'IGNORADO') correspondeStatus = linha.classList.contains('row-skip');

                linha.style.display = (correspondeTexto && correspondeStatus) ? '' : 'none';
            }});
        }}
    </script>
</body>
</html>"""

        pasta_destino = os.path.dirname(caminho_arquivo)
        if pasta_destino and not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino, exist_ok=True)

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(html_content)

    @staticmethod
    def gerar_markdown(dados: Dict[str, Any], caminho_arquivo: str) -> None:
        """Gera um arquivo de resumo em Markdown legível e conciso."""
        linhas = [
            "# Relatório de Evidências de Testes Automatizados - GeoAlvo",
            "",
            f"**Data da Execução:** {dados['data_hora']}  ",
            f"**Ambiente:** {dados['sistema_operacional']} | Python {dados['python_versao']} ({dados['arquitetura']})  ",
            f"**Duração Total:** {dados['duracao_segundos']}s  ",
            "",
            "## Resumo Executivo",
            "",
            "| Métrica | Quantidade | Percentual |",
            "| :--- | :---: | :---: |",
            f"| **Total de Testes** | {dados['total']} | 100% |",
            f"| ✅ **Aprovados** | {dados['sucessos']} | {dados['taxa_sucesso']}% |",
            f"| ❌ **Falhas** | {dados['falhas']} | {round(dados['falhas']/max(1,dados['total'])*100, 1)}% |",
            f"| ⚠️ **Erros** | {dados['erros']} | {round(dados['erros']/max(1,dados['total'])*100, 1)}% |",
            f"| ⏸️ **Ignorados** | {dados['ignorados']} | {round(dados['ignorados']/max(1,dados['total'])*100, 1)}% |",
            "",
            "---",
            "",
            "## Detalhes das Execuções",
            "",
            "| # | Módulo | Classe | Teste | Status | Duração |",
            "| :-: | :--- | :--- | :--- | :-: | -: |",
        ]

        for i, ev in enumerate(dados["evidencias"], 1):
            st_icone = "✅ OK" if ev["status"] == "SUCESSO" else ("❌ FALHA" if ev["status"] == "FALHA" else ("⚠️ ERRO" if ev["status"] == "ERRO" else "⏸️ SKIP"))
            dur_ms = f"{ev['tempo_execucao']*1000:.1f}ms"
            linhas.append(f"| {i} | `{ev['modulo']}` | {ev['classe']} | `{ev['nome']}` | {st_icone} | {dur_ms} |")

        if dados["falhas"] > 0 or dados["erros"] > 0:
            linhas.extend([
                "",
                "---",
                "",
                "## Detalhamento de Falhas e Erros",
                "",
            ])
            for ev in dados["evidencias"]:
                if ev["status"] in ("FALHA", "ERRO"):
                    linhas.extend([
                        f"### {ev['status']}: `{ev['test_id']}`",
                        f"**Mensagem:** {ev['mensagem_erro']}",
                        "```python",
                        ev["traceback_erro"].strip(),
                        "```",
                        "",
                    ])

        pasta_destino = os.path.dirname(caminho_arquivo)
        if pasta_destino and not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino, exist_ok=True)

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas) + "\n")

    @staticmethod
    def gerar_log(dados: Dict[str, Any], caminho_arquivo: str) -> None:
        """Gera um arquivo de log estruturado."""
        linhas = [
            f"=== RELATORIO DE EVIDENCIAS DE TESTES - {dados['data_hora']} ===",
            f"Total: {dados['total']} | Sucessos: {dados['sucessos']} | Falhas: {dados['falhas']} | Erros: {dados['erros']} | Ignorados: {dados['ignorados']}",
            f"Taxa de Sucesso: {dados['taxa_sucesso']}% | Duracao: {dados['duracao_segundos']}s",
            f"Ambiente: {dados['sistema_operacional']} - Python {dados['python_versao']}",
            "-" * 80,
        ]

        for ev in dados["evidencias"]:
            linhas.append(f"[{ev['status']}] {ev['test_id']} ({ev['tempo_execucao']*1000:.1f}ms)")
            if ev["traceback_erro"]:
                linhas.append("  Detalhes:\n" + "  " + ev["traceback_erro"].replace("\n", "\n  "))

        linhas.append("-" * 80)
        linhas.append(f"Fim da execucao - Status Geral: {'APROVADO' if dados['falhas'] == 0 and dados['erros'] == 0 else 'REPROVADO'}\n")

        pasta_destino = os.path.dirname(caminho_arquivo)
        if pasta_destino and not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino, exist_ok=True)

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas))


def executar_testes(
    alvo: Optional[str] = None,
    pasta_destino: Optional[str] = None,
    padrao: str = "test*.py",
) -> Dict[str, Any]:
    """
    Executa os testes e gera as evidências na pasta do executável.
    
    :param alvo: Arquivo ou módulo específico (ex: 'tests/test_ativo_imobilizado.py'). Se None, executa discover.
    :param pasta_destino: Diretório onde serão gravadas as evidências. Se None, usa a pasta do executável GeoAlvo.exe (PASTA_RAIZ).
    :param padrao: Padrão de descoberta de arquivos de teste.
    :return: Dicionário consolidado com as métricas da execução.
    """
    if not pasta_destino:
        pasta_destino = PASTA_RAIZ

    pasta_evidencias_hist = os.path.join(pasta_destino, "evidencias_testes")
    os.makedirs(pasta_evidencias_hist, exist_ok=True)

    loader = unittest.TestLoader()
    if alvo:
        if os.path.isfile(alvo):
            modulo_ou_dir = alvo.replace("\\", "/").rstrip(".py").replace("/", ".")
            suite = loader.loadTestsFromName(modulo_ou_dir)
        else:
            suite = loader.loadTestsFromName(alvo)
    else:
        suite = loader.discover(start_dir=os.path.join(PASTA_RAIZ, "tests"), pattern=padrao)

    coletor = ColetorEvidenciasTestResult(verbosity=2)
    suite.run(coletor)
    dados = coletor.consolidar_metricas()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Arquivo HTML datado na pasta de histórico
    caminho_html_hist = os.path.join(pasta_evidencias_hist, f"evidencia_testes_{timestamp}.html")
    GeradorRelatorioEvidencias.gerar_html(dados, caminho_html_hist)

    # 2. Arquivo HTML fixo na raiz (ao lado do executável GeoAlvo.exe)
    caminho_html_fixo = os.path.join(pasta_destino, "ultima_evidencia_testes.html")
    GeradorRelatorioEvidencias.gerar_html(dados, caminho_html_fixo)

    # 3. Resumo Markdown na raiz
    caminho_md = os.path.join(pasta_destino, "RELATORIO_EVIDENCIAS_TESTES.md")
    GeradorRelatorioEvidencias.gerar_markdown(dados, caminho_md)

    # 4. Arquivo de log datado na pasta de histórico
    caminho_log = os.path.join(pasta_evidencias_hist, f"evidencia_testes_{timestamp}.log")
    GeradorRelatorioEvidencias.gerar_log(dados, caminho_log)

    print("\n" + "=" * 70)
    print(f"[OK] EVIDENCIAS DE TESTES GERADAS COM SUCESSO!")
    print(f"Total: {dados['total']} | Aprovados: {dados['sucessos']} | Falhas: {dados['falhas']} | Erros: {dados['erros']}")
    print(f"Taxa de Sucesso: {dados['taxa_sucesso']}% em {dados['duracao_segundos']}s")
    print(f"Pasta do Executavel: {pasta_destino}")
    print(f"Relatorio Visual (HTML): {caminho_html_fixo}")
    print(f"Resumo (Markdown): {caminho_md}")
    print(f"Historico Datado: {caminho_html_hist}")
    print("=" * 70 + "\n")

    return dados


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executor de Testes com Evidências - GeoAlvo")
    parser.add_argument("alvo", nargs="?", default=None, help="Arquivo de teste ou módulo específico (opcional)")
    parser.add_argument("--destino", default=None, help="Pasta de destino das evidências (padrão: pasta do executável)")
    parser.add_argument("--pattern", default="test*.py", help="Padrão de busca para discover (padrão: test*.py)")

    args = parser.parse_args()
    resultado = executar_testes(alvo=args.alvo, pasta_destino=args.destino, padrao=args.pattern)

    # Código de saída 0 se nenhum erro/falha, 1 se houver problemas
    codigo_saida = 0 if (resultado["falhas"] == 0 and resultado["erros"] == 0) else 1
    sys.exit(codigo_saida)
