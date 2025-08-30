import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environments';
import { Observable } from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class FraudServicesService {
  private readonly url: string = environment.urlApi;

  constructor(
    private http: HttpClient,

  ) { }

  public predict(data: any): Observable<any> {
    return this.http.post<any>(`${this.url}/predict`, data);
  }

  public predictBatch(data: any): Observable<any> {
    return this.http.post<any>(`${this.url}/predict_batch`, { "transactions": data});
  }

  public generateTransaction(number: number = 10): Observable<any> {
    return this.http.get<any>(`${this.url}/generate_transactions?number=${number}`);
  }
}
