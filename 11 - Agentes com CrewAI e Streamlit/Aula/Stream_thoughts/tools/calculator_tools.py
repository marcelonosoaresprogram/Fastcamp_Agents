from langchain.tools import tool


class CalculatorTools():
  # Classe que fornece ferramentas para realizar cálculos matemáticos durante o planejamento da viagem

  @tool("Make a calcualtion")
  def calculate(operation):
    """Useful to perform any mathematical calculations, 
    like sum, minus, multiplication, division, etc.
    The input to this tool should be a mathematical 
    expression, a couple examples are `200*7` or `5000/2*10`
    """
    # Ferramenta que executa operações matemáticas usando a função eval do Python
    # Útil para calcular orçamentos, converter moedas, estimar custos totais, etc.
    # Recebe uma expressão matemática como string e retorna o resultado calculado
    return eval(operation)
