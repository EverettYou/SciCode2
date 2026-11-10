// Midpoint Strang integrator for the explicitly declared physical forward model.
#include <algorithm>
#include <chrono>
#include <cmath>
#include <complex>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>
int main(int argc,char**argv){
 if(argc!=4)return 2;auto start=std::chrono::steady_clock::now();std::ifstream in(argv[1]);double T=std::stod(argv[2]);int steps=std::stoi(argv[3]);
 int N,nJ,n,L,g;in>>N>>nJ>>n>>L>>g;if(N<0||N>20||steps<1||T<=0)return 3;
 std::vector<double>h(N);for(auto&v:h)in>>v;
 struct Edge{int a,b;double J;};std::vector<Edge>J(nJ);for(auto&e:J)in>>e.a>>e.b>>e.J;
 std::vector<int>roots(n),allroots(L),owners(N);for(auto&v:roots)in>>v;for(auto&v:allroots)in>>v;for(auto&v:owners)in>>v;
 std::vector<unsigned char>optimal(1u<<n,0);for(int i=0;i<g;i++){unsigned q;in>>q;optimal[q]=1;}if(!in)return 4;
 size_t S=1ull<<N;std::vector<double>E(S);std::vector<unsigned char>success(S),broken(S);
 double minE=1e300;
 for(size_t x=0;x<S;x++){
  double energy=0;for(int q=0;q<N;q++)energy+=h[q]*(((x>>q)&1)?1:-1);
  for(auto&e:J)energy+=e.J*((((x>>e.a)^(x>>e.b))&1)?-1:1);E[x]=energy;minE=std::min(minE,energy);
  unsigned original=0;for(int i=0;i<n;i++)original|=((x>>roots[i])&1)<<i;success[x]=optimal[original];
  bool bad=false;for(int q=0;q<N;q++)if(((x>>q)&1)!=((x>>allroots[owners[q]])&1)){bad=true;break;}broken[x]=bad;
 }
 double amp=1/std::sqrt(double(S));std::vector<std::complex<double>>psi(S,{amp,0});double dt=T/steps;
 auto diagonal=[&](double angle){for(size_t x=0;x<S;x++){double v=-angle*E[x];psi[x]*=std::complex<double>(std::cos(v),std::sin(v));}};
 diagonal(dt/(4*steps));
 for(int k=0;k<steps;k++){
  double angle=dt*(1-(k+.5)/steps),c=std::cos(angle),s=std::sin(angle);
  for(int q=0;q<N;q++){size_t stride=1ull<<q;
   for(size_t base=0;base<S;base+=2*stride)for(size_t j=0;j<stride;j++){
    auto a=psi[base+j],b=psi[base+j+stride];psi[base+j]=c*a+std::complex<double>(0,s)*b;psi[base+j+stride]=c*b+std::complex<double>(0,s)*a;
   }
  }
  diagonal(k+1<steps?dt*double(k+1)/steps:dt*(1-.5/steps)/2);
 }
 double norm=0,p=0,b=0,ground=0;
 for(size_t x=0;x<S;x++){double weight=std::norm(psi[x]);norm+=weight;if(success[x])p+=weight;if(broken[x])b+=weight;if(E[x]<=minE+1e-8)ground+=weight;}
 double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
 std::cout<<std::setprecision(17)<<"{\"N\":"<<N<<",\"T\":"<<T<<",\"steps\":"<<steps<<",\"norm\":"<<norm<<",\"original_optimal\":"<<p<<",\"chain_broken\":"<<b<<",\"full_ground\":"<<ground<<",\"seconds\":"<<seconds<<"}\n";
}
