unit unt_matchcode_service;

interface

uses
  System.SysUtils, System.Classes, unt_matchcode_types, unt_matchcode_repository;

type
  IMatchCodeService = interface
    ['{8D5F9A1B-3C4E-4F2A-A814-1B2C3D4E5F6A}']
    function ObterNomeUsuario(const AUsucod: string): string;
    function ObterNomeEntidade(const AEntcod: string): string;
    function UnificarUsuarios(const AOrigem, ADestino: string): TResultadoMatchCode;
    function UnificarEntidades(const AOrigem, ADestino: string): TResultadoMatchCode;
  end;

  TMatchCodeService = class(TInterfacedObject, IMatchCodeService)
  private
    FRepo: IMatchCodeRepository;
  public
    constructor Create(ARepository: IMatchCodeRepository);
    function ObterNomeUsuario(const AUsucod: string): string;
    function ObterNomeEntidade(const AEntcod: string): string;
    function UnificarUsuarios(const AOrigem, ADestino: string): TResultadoMatchCode;
    function UnificarEntidades(const AOrigem, ADestino: string): TResultadoMatchCode;
  end;

implementation

constructor TMatchCodeService.Create(ARepository: IMatchCodeRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise Exception.Create('TMatchCodeService: Repositório é obrigatório.');
  FRepo := ARepository;
end;

function TMatchCodeService.ObterNomeUsuario(const AUsucod: string): string;
begin
  if Trim(AUsucod) = '' then Exit('');
  Result := FRepo.ObterNomeUsuario(Trim(AUsucod));
end;

function TMatchCodeService.ObterNomeEntidade(const AEntcod: string): string;
begin
  if Trim(AEntcod) = '' then Exit('');
  Result := FRepo.ObterNomeEntidade(Trim(AEntcod));
end;

function TMatchCodeService.UnificarUsuarios(const AOrigem, ADestino: string): TResultadoMatchCode;
var
  Orig, Dest: string;
begin
  Result.Sucesso := False;
  Result.RegistrosMigrados := 0;

  Orig := Trim(AOrigem);
  Dest := Trim(ADestino);

  if (Orig = '') or (Dest = '') then
  begin
    Result.Mensagem := 'Usuários de origem e destino devem ser informados.';
    Exit;
  end;

  if SameText(Orig, Dest) then
  begin
    Result.Mensagem := 'O usuário de origem não pode ser idêntico ao de destino.';
    Exit;
  end;

  if FRepo.ObterNomeUsuario(Orig) = '' then
  begin
    Result.Mensagem := Format('Usuário de origem "%s" não localizado.', [Orig]);
    Exit;
  end;

  if FRepo.ObterNomeUsuario(Dest) = '' then
  begin
    Result.Mensagem := Format('Usuário de destino "%s" não localizado.', [Dest]);
    Exit;
  end;

  Result := FRepo.UnificarUsuarios(Orig, Dest);
end;

function TMatchCodeService.UnificarEntidades(const AOrigem, ADestino: string): TResultadoMatchCode;
var
  Orig, Dest: string;
begin
  Result.Sucesso := False;
  Result.RegistrosMigrados := 0;

  Orig := Trim(AOrigem);
  Dest := Trim(ADestino);

  if (Orig = '') or (Dest = '') then
  begin
    Result.Mensagem := 'Entidades de origem e destino devem ser informadas.';
    Exit;
  end;

  if SameText(Orig, Dest) then
  begin
    Result.Mensagem := 'A entidade de origem não pode ser idêntica à de destino.';
    Exit;
  end;

  if FRepo.ObterNomeEntidade(Orig) = '' then
  begin
    Result.Mensagem := Format('Entidade de origem "%s" não localizada.', [Orig]);
    Exit;
  end;

  if FRepo.ObterNomeEntidade(Dest) = '' then
  begin
    Result.Mensagem := Format('Entidade de destino "%s" não localizada.', [Dest]);
    Exit;
  end;

  Result := FRepo.UnificarEntidades(Orig, Dest);
end;

end.
