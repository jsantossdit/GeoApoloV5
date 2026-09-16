unit uEntidadeService;

interface

uses
  FireDAC.Comp.Client, uEntidade, System.SysUtils;

type
  TEntidadeService = class
  private
    FConn: TFDConnection;
  public
    constructor Create(AConn: TFDConnection);

    procedure GravarTela1(const Ent: TEntidade);
    procedure GravarTela2(const Ent: TEntidade);
    procedure GravarTela3(const Ent: TEntidade);
    procedure GravarTela4(const Ent: TEntidade);
    procedure GravarTela5(const Ent: TEntidade);
    procedure GravarTela6(const Ent: TEntidade);
    procedure GravarTela7(const Ent: TEntidade);
  end;

implementation

{ TEntidadeService }

constructor TEntidadeService.Create(AConn: TFDConnection);
begin
  FConn := AConn;
end;

procedure TEntidadeService.GravarTela1(const Ent: TEntidade);
var
  Qry: TFDQuery;
begin
  Ent.ValidarCamposObrigatorios;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'UPDATE USER_geoapolo_entidade SET ' +
      'geoentnome = :nome, geoentnomefantasia = :nomefantasia, ' +
      'geoentender = :endereco, geoenderno = :numero, geoentbair = :bairro, ' +
      'geocidcod = :cidade, geoentcep = :cep, geoentdatacad = :datacad ' +
      'WHERE geoentcod = :codigo';

    Qry.ParamByName('codigo').AsString := Ent.GeoEntCod;
    Qry.ParamByName('nome').AsString := Ent.Nome;
    Qry.ParamByName('nomefantasia').AsString := Ent.NomeFantasia;
    Qry.ParamByName('endereco').AsString := Ent.Endereco;
    Qry.ParamByName('numero').AsString := Ent.Numero;
    Qry.ParamByName('bairro').AsString := Ent.Bairro;
    Qry.ParamByName('cidade').AsString := Ent.CidadeCod;
    Qry.ParamByName('cep').AsString := Ent.CEP;
    Qry.ParamByName('datacad').AsDate := Ent.DataCadastro;

    Qry.ExecSQL;
  finally
    Qry.Free;
  end;
end;

procedure TEntidadeService.GravarTela2(const Ent: TEntidade);
begin
  // Exemplo: Atualizar informações de pai/mãe e filhos
end;

procedure TEntidadeService.GravarTela3(const Ent: TEntidade);
begin
  // Exemplo: Atualizar informações financeiras (banco, diocese, etc.)
end;

procedure TEntidadeService.GravarTela4(const Ent: TEntidade);
begin
  // Exemplo: Atualizar informações de cobrança e entrega
end;

procedure TEntidadeService.GravarTela5(const Ent: TEntidade);
begin
  // Exemplo: Atualizar endereço de cobrança
end;

procedure TEntidadeService.GravarTela6(const Ent: TEntidade);
begin
  // Exemplo: Gravar contatos vinculados
end;

procedure TEntidadeService.GravarTela7(const Ent: TEntidade);
begin
  // Exemplo: Inserir categoria da entidade
end;

{Entidade.RegistrationDate := mskdtcadastro.Text;
Entidade.BirthDate := mskdtnascimento.Text;}

end.

