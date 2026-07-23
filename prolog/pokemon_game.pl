:-ensure_loaded("pokemon_list.pl").
:-ensure_loaded("pokemon_info_attacks.pl").
:-ensure_loaded("pokemon_route.pl").

player_starts(0,0).

% TO DO

inside_limits(X,Y) :-
    (X >= 0, X =< 4, Y >= 0, Y =< 4).

is_neighbor(X1,Y1,X2,Y2) :-
    (X2 is X1 + 1, Y2 is Y1).
is_neighbor(X1,Y1,X2,Y2) :-
    (X2 is X1 - 1, Y2 is Y1).
is_neighbor(X1,Y1,X2,Y2) :-
    (X2 is X1, Y2 is Y1 + 1).
is_neighbor(X1,Y1,X2,Y2) :-
    (X2 is X1, Y2 is Y1 - 1).

next_rooms(X,Y,Rooms) :-
    route(M),
    findall(
        [Id, Name, Level, NX, NY, Types],
        (
            is_neighbor(X, Y, NX, NY),
            inside_limits(NX, NY),
            elemento_indice(NX, M, Linha),
            elemento_indice(NY, Linha, (Id, Level)),
            Id \= 0,
            pokemon(Id, Name, Types)
        ),
        Rooms
    ).

elemento_indice(0, [H|_], H).
elemento_indice(N, [_|T], Elem) :-
        N > 0,
        N1 is N - 1,
        elemento_indice(N1, T, Elem).