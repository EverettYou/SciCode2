// Finite-budget CLASSICAL random-scan heat-bath anneal. No quantum simulation.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <utility>
#include <vector>
struct RNG {
  uint64_t x;
  uint64_t next() { x += 0x9e3779b97f4a7c15ULL; uint64_t z=x; z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31); }
  size_t bounded(size_t n) {uint64_t threshold=-uint64_t(n)%uint64_t(n),v;do{v=next();}while(v<threshold);return v%n;}
  double uniform(){return ((next()>>11)+0.5)*0x1.0p-53;}
};
int main(int argc,char** argv){
 if(argc!=3)return 2;std::ifstream in(argv[1]);std::ofstream out(argv[2]);
 int N,E,n,m,K,reps,nb;double beta,opt;uint64_t seed;int hasopt;
 if(!(in>>N>>E>>n>>m>>K>>reps>>nb>>beta>>seed>>hasopt>>opt))return 3;
 std::vector<double> h(N),weights(n);for(auto &v:h)in>>v;
 std::vector<std::vector<std::pair<int,double>>> adj(N);
 for(int k=0;k<E;k++){int q,r;double v;in>>q>>r>>v;adj[q].push_back({r,v});adj[r].push_back({q,v});}
 std::vector<int> roots(n);for(auto &v:roots)in>>v;
 std::vector<std::vector<int>> rows(m);std::vector<int>s(m);
 for(int r=0;r<m;r++){int d;in>>d;rows[r].resize(d);for(auto &v:rows[r])in>>v;in>>s[r];}
 for(auto &v:weights)in>>v;
 std::vector<std::pair<int,int>> chains(K);for(auto &e:chains)in>>e.first>>e.second;
 std::vector<uint64_t> budgets(nb);for(auto &v:budgets)in>>v;
 if(!in||N<=0||n>64)return 4;
 out<<"attempts,replica,consistent,feasible,optimal,cost,error_mask,physical_bits\n"<<std::setprecision(17);
 for(auto steps:budgets)for(int rep=0;rep<reps;rep++){
  RNG rng{seed ^ (uint64_t(rep+1)*0xd2b74407b1ce6e93ULL) ^ (steps*0xca5a826395121157ULL)};
  std::vector<int8_t> z(N);for(auto &v:z)v=(rng.next()&1)?1:-1;
  for(uint64_t t=0;t<steps;t++){
   size_t q=rng.bounded(N);double field=h[q];for(auto e:adj[q])field+=e.second*z[e.first];
   double delta=-2.0*z[q]*field,b=beta*(double(t)+0.5)/double(steps);
   double prob=1.0/(1.0+std::exp(b*delta));if(rng.uniform()<prob)z[q]=-z[q];
  }
  std::vector<int> error(n);uint64_t mask=0;double cost=0;
  for(int i=0;i<n;i++){error[i]=z[roots[i]]==1;if(error[i]){mask|=1ULL<<i;cost+=weights[i];}}
  bool consistent=true,feasible=true;for(auto e:chains)if(z[e.first]!=z[e.second]){consistent=false;break;}
  for(int r=0;r<m;r++){int parity=0;for(int i:rows[r])parity^=error[i];if(parity!=s[r]){feasible=false;break;}}
  int optimal=hasopt?(feasible&&std::abs(cost-opt)<1e-9):-1;
  out<<steps<<','<<rep<<','<<consistent<<','<<feasible<<','<<optimal<<','<<cost<<','<<std::hex<<mask<<std::dec<<',';
  for(auto v:z)out<<(v==1?'1':'0');out<<'\n';
 }
 return 0;
}
