unit uEntidade;

interface

uses
  System.SysUtils, Vcl.Dialogs, System.DateUtils;

type
  TEntidade = class
  private
    FGeoEntCod: string;
    FTipoTratcod: string;
    FNome: string;
    FNomeFantasia: string;
    FCEP: string;
    FLogradouro: string;
    FEndereco: string;
    FNumero: string;
    FComplemento: string;
    FBairro: string;
    FCidadeCod: string;
    FNomeCidade: string;
    FUFSigla: string;
    FCaixaPostal: string;
    FGenero: string;
    FFalecido: string;
    FLocalReferencia: string;
    FTipoIdentificacao: string;
    FEstadoCivil: string;
    FDataCadastro: TDate;
    FDataAniversario: TDate;
    FCargoCodEstr: string;
    FTipoFJ: string;
    FEscolaridade: string;
    FRegiaoCodEstr: string;
    FConceito: string;
    FDataNascimento: TDate;

    procedure SetCidadeCod(const Value: string);  // <--- Setter criado aqui

  public
    property GeoEntCod: string read FGeoEntCod write FGeoEntCod;
    property Tipotratcod: string read FTipotratcod write FTipotratcod;
    property Nome: string read FNome write FNome;
    property NomeFantasia: string read FNomeFantasia write FNomeFantasia;
    property CEP: string read FCEP write FCEP;
    property Logradouro: string read FLogradouro write FLogradouro;
    property Endereco: string read FEndereco write FEndereco;
    property Numero: string read FNumero write FNumero;
    property Complemento: string read FComplemento write FComplemento;
    property Bairro: string read FBairro write FBairro;

    // Aqui usamos o setter em vez de acesso direto
    property CidadeCod: string read FCidadeCod write SetCidadeCod;
    property NomeCidade: string read FNomeCidade write FNomeCidade;

    property Estado: string read FUFSigla write FUFSigla;
    property CaixaPostal: string read FCaixaPostal write FCaixaPostal;
    property Genero: string read FGenero write FGenero;
    property Falecido: string read FFalecido write FFalecido;
    property LocalReferencia: string read FLocalReferencia write FLocalReferencia;

    property TipoIdentificacao: string read FTipoIdentificacao write FTipoIdentificacao;
    property EstadoCivil: string read FEstadoCivil write FEstadoCivil;
    property DataAniversario: TDate read FDataAniversario write FDataAniversario;
    property DataCadastro: TDate read FDataCadastro write FDataCadastro;
    property Escolaridade: string read FEscolaridade write FEscolaridade;
    property CargoCodEstr: string read FCargoCodEstr write FCargoCodEstr;
    property TipoFJ: string read FTipoFJ write FTipoFJ;
    property Conceito: string read FConceito write FConceito;
    property RegiaoCodEstr: string read FRegiaoCodEstr write FRegiaoCodEstr;

    procedure ValidarCamposObrigatorios;
    function Idade: string;
    property DataNascimento: TDate read FDataAniversario write FDataAniversario;

  end;

function CalcularIdade(const DataNasc: TDate): string; export;

implementation

uses
  FireDAC.Comp.Client, unt_dados; // <-- importante: o módulo onde está FDConnection

{ ===================================== }
{   Implementação do setter CidadeCod   }
{ ===================================== }
procedure TEntidade.SetCidadeCod(const Value: string);
var
  Qry: TFDQuery;
begin
  FCidadeCod := Value;

  if Trim(Value) = '' then
  begin
    FNomeCidade := '';
    Exit;
  end;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := Modulo_Dados.fdbanco; // sua conexão principal
    Qry.SQL.Text := 'SELECT cidnomecomp FROM USER_geoapolo_cidades WHERE geocidcod = :cod';
    Qry.ParamByName('cod').AsString := Value;
    Qry.Open;

    if not Qry.IsEmpty then
      FNomeCidade := Qry.FieldByName('cidnomecomp').AsString
    else
      FNomeCidade := '*** Cidade não encontrada ***';
  finally
    Qry.Free;
  end;
end;

{ ===================================== }
{   Validação dos campos obrigatórios   }
{ ===================================== }
procedure TEntidade.ValidarCamposObrigatorios;
begin
  if Trim(FGeoEntCod) = '' then
    raise Exception.Create('O código da entidade é obrigatório.');

  if Trim(FNome) = '' then
    raise Exception.Create('O nome da entidade é obrigatório.');

  if Trim(FEndereco) = '' then
    raise Exception.Create('O endereço da entidade é obrigatório.');

  if Trim(FCidadeCod) = '' then
    raise Exception.Create('O código da cidade é obrigatório.');

  if FDataCadastro = 0 then
    raise Exception.Create('A data de cadastro é obrigatória.');
end;

function CalcularIdade(const DataNasc: TDate): string;
begin
  Result := IntToStr(YearsBetween(Date, DataNasc));
end;

function TEntidade.Idade: string;
begin
  Result := CalcularIdade(FDataNascimento);
end;
{procedure TEntidade.SetRegistrationDate(Value: string);
var
  dt: TDate;
begin
  dt := TDateUtils.Parse(Value);
  if dt <= 0 then
     raise EValidationError.Create('Data de cadastro inválida.');
  FRegistrationDate := dt;
end;}

end.

