# Problem

Aplikacja do zarządzania rachunkami musi pozwalać na audytowalność oraz zapewnić możliwość reprezentacji danych na wiele
różnych sposóbów zależnie od potrzeb klienckich - musi też wspierać wysoką skalowalność tak aby obsłużyć duży ruch.
Należy również uwzględnić poziom skomplikowania rozwiązania - tak aby mogły je rozwijać osoby posiadające ograniczone
doświadczenie programistyczne. Należy rozpoznać możliwe podejścia spełniające powyższe wymagania. Oraz stworzyć schemat
komunikacji komponentów aplikacji, oraz uszczegółowić wykorzystane technologie na poszczególnych warstwach tak aby
umożliwić późniejszy rozwój funkcjonalności.

## Rozważane opcje

### Backend

* Architektura monolityczna MVC
* Architektura monolityczna heksagonalna
* Architektura mikroserwisowa
* Architektura oparta o zdarzenia

### Frontend

* SSR
* SPA
* SPA + PWA
* SPA + PWA + MicroFrontends

## Analiza rozważanych podejść

### Architektura monolityczna MVC

Jest to klasyczne podejście. Jego główną zaletą jest prostota implementacji, a również szybkość. Jednakże z jej pomocą
trudno jest zapewnić audytowalność - wymaga to dodatkowej pracy, podobnie będzie z zapewnieniem zróżnicowanej
reprezentacji danych, a ona z kolei pociągnie ograniczenie skalowalności aplikacji. Dlatego jest to rozwiązanie
całkowicie niedostosowane do wymagań i już na wstępie można je odrzucić.

### Architektura monolityczna heksagonalna

Jest to podejście nieco bardziej skomplikowane od omawianego wcześniej, choć nie wymaga większej ilości umiejętności a
zwiększonej dyscypliny programistów.
![](heksagon.png)

Zapewnia zwiększoną ilość i łatwość w tworzeniu wielu reprezentacji danych gdyż są luźno ze sobą powiązane. Stanowi też
dobry punkt wejściowy by zastosować podejście EventSourcingu, który zapewni audytowalność.

### Architektura mikroserwisowa

Architektura mikroserwisowa to wiele skomunikowanych ze sobą mniejszych aplikacji o ograniczonej odpowiedzialności.
Zapewnia wysoką skalowalność jednak zwiększone koszty infrastrukturalne, oraz wydłuża i komplikuje wytwarzanie
oprogramowania.

### Architektura oparta o zdarzenia

Wspomniany wcześniej EventSourcing jest podejściem opierania komunikacji pomiędzy elementami pojedynczej aplikacji oraz
wielu aplikacji uporządkowanymi w czasie oraz przypisanymi do encji zdarzeniami. Zapewnia między innymi pełną
audytowalność tego co dzieje się w systemie, oraz pozwala na łatwe diagnozowanie różnego rodzaju problemów i naprawę
ich. Jest to jednak dość trudna w implementacji technika.

### SSR

"Server Side Rendering" - obciążające serwery podejście. Łatwy w implementacji jednak odchodzi się od tego podejścia ze
względu na niską responsywność oraz atrakcyjność przez klientów końcowych.

### SPA

"Single Page Application" - sposób wytwarzania aplikacji webowych który sprawia wrażenie płynności, oraz w całości
renderowany jest przez klienta końcowego. Odciąża serwer, który wykorzystywany jest w tej sytuacji jedynie do
dostarczania danych do wyświetlenia. Samą aplikację typu SPA można hostować na zupełnie innej maszynie.

### SPA + PWA

W przeciwieństwie do SPA aplikacja webowa może działać w trybie offline co sprawia że można ją również traktować jak
aplikację mobilną. Nieco bardziej zaawansowane podejście, jednak zwiększające niskim kosztem użyteczność oraz
poszerzające kliencką grupę docelową.

### SPA + PWA + MicroFrontends

Dodając podejście MicroFrontends można całkowicie uniezależnić moduły, czy mikroserwisy również na warstwie prezentacji.
Przydatne gdy chcemy testować różne wersje prezentacyjne oraz ich odbiór przez użytkowników w testach AB. Przykładowo
chcąc sprawdzić jaki kolor przycisku na stronie zwiększy jego konwersję.

# Decyzja

Biorąc pod uwagę wszystkie podejścia najsensowniejszym sposobem wydaje się kompromis oraz lawirowanie pomiędzy
większością z nich tak aby sprostać wszystkim wymaganiom, zachowując przy tym stosunkowo niskie skomplikowanie oraz
możliwości rozwoju systemu.

Początkowo stosowane powinno by podejście monolityczne heksagonalne, lecz z podziałem pionowym, tak aby wszystko
działało w obrębie jednej aplikacji jednak moduły biznesowe/funkcjonalne były bardzo luźno ze sobą związane. Pozwoli to
na różne sposoby reprezentacji, a w przyszłości na łatwą migrację w stronę mikroserwisową bez ponoszenia początkowego
kosztu infrastrukturalnego.

Chcąc zapewnić audytowalność jak najszybciej powinno zostać wdrożone podejście oparte o zdarzenia.

Co do warstwy prezentacji rekomendowane jest podejście SPA, gdyż pozwoli na umiarkowanie szybki rozwój aplikacji.
Niestety wiąże się to z przepisaniem istniejącego rozwiązania. Późniejsze dostosowanie go do PWA tak aby stworzyć
aplikacje mobilne powinno być już relatywnie proste. Co się tyczy MicroFrontends - będzie ono możliwe do wdrożenia
jednak jest to dość zaawansowana technika i nie ma to większego sensu przy obecnym zakresie funkcjonalności. Gdy ilość
funkcji mocno przyrośnie warto się nad tym zastanowić.