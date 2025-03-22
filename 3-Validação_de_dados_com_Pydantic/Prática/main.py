from fastapi import FastAPI, Path, Query, HTTPException, status
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
)

class Stock():
    id: int
    name: str
    category: str
    quantity:int

    def __init__(self, id, name, category, quantity):
        self.id = id
        self.name = name
        self.category = category
        self.quantity = quantity

class Stock_Request(BaseModel):
    id: int = Field(
        description="É necessário fornecer ao sistema o identificador referente ao produto",
        )
    name: str = Field(
        description= "nome do produto",
        examples=["Absolut Vodka", "Tanqueray London Dry Gin"]
    )
    category: str = Field(
        description= "Tipo de produto, bebida, equipamento ou insumo",
        examples=["Laranja","Vodka","Gin","Whisky","Energético,","Refrigerante"]
    )
    quantity: int = Field()

    class Config:
        json_schema_extra = {
            'example':{
                'id': 10,
                'name': 'Suco de uva',
                'category': 'Bebida',
                'quantity': 4
                }
            }
app = FastAPI()
#Lista que irá armazenar os valores com o cadastro ou atualização do estoque
Lista = [
    Stock(1, "Limão", "Insumo", 2),
    Stock(12, "Sal", "Insumo",1)
]
#Método post para adicionar item a lista
@app.post('/stock/', status_code=status.HTTP_201_CREATED)
async def create_stock(stock_request: Stock_Request):
    new_stock = Stock(**stock_request.model_dump())
    Lista.append(new_stock)
    return new_stock
#método get para visualizar os itens da lista
@app.get('/stock/', status_code=status.HTTP_201_CREATED)
async def read_all_stock():
    return Lista
#método get para pesquisar um item único na lista
@app.get('/stock/{stock_id}', status_code= status.HTTP_200_OK)
async def read_stock(stock_id: int = Path(gt=0)):
    for stock in Lista:
        if stock.id == stock_id:
            return stock
    raise HTTPException(status_code=404, detail='Stock not found')
#método put para atualizar um produto na lista
@app.put('/stock/{stock_id}', status_code=status.HTTP_200_OK)
async def update_stock(stock_id:int, stock_request:Stock_Request):
    for i, stock in enumerate(Lista):
        if stock.id == stock_id:
            updated_stock = Stock(
                id = stock_id,
                name = stock_request.name,
                category = stock_request.category,
                quantity = stock_request.quantity
            )
            Lista[i] = updated_stock
            return updated_stock
    raise HTTPException(status_code= 404, detail= 'Stock not found')

@app.delete('/stock/{stock_id}', status_code= status.HTTP_204_NO_CONTENT)
async def delete_stock(stock_id:int):
    for i, stock in enumerate(Lista):
        if stock.id == stock_id:
            Lista.pop(i)
            return
    raise HTTPException(status_code=404, detail= 'Stock not found')
