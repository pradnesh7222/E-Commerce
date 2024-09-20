from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.forms import ProductForm
from core.models import Product



def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
        else:
            print('Product is not added...')
            return render(request, 'core/add_product.html', {'form': form})
    else:
        form = ProductForm()
        return render(request,'core/add_product.html',{'form':form})
    





@login_required
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id,)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ProductForm(instance=product)
    return render(request, 'seller/edit_product.html', {'form': form})


@login_required
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('index')
    return render(request, 'seller/delete_product.html', {'product': product})